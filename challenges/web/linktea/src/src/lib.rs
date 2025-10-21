pub mod auth;
pub mod models;
pub mod routes;
pub mod utils;

use crate::models::user::User;
use axum::routing::{get, post};
use axum::{middleware, Router};
use memory_serve::{load_assets, CacheControl, MemoryServe};
use sqlx::sqlite::SqliteConnectOptions;
use sqlx::SqlitePool;
use std::sync::Arc;
use std::time::Duration;
use tokio::signal;
use tower_http::timeout::TimeoutLayer;
use tower_http::trace::TraceLayer;
use tracing::info;

#[derive(Clone)]
pub struct AppState {
    pub db: SqlitePool,
    pub jwt_secret: String,
    pub moderator_secret: String,
    pub flag: String,
}

pub fn configure_router(pool: &SqlitePool, flag: &str, moderator_password: &str) -> Router {
    let state = Arc::new(AppState {
        db: pool.clone(),
        jwt_secret: utils::generate_id(64),
        moderator_secret: moderator_password.to_string(),
        flag: flag.to_string(),
    });

    let memory_router = MemoryServe::new(load_assets!("./web/dist"))
        .html_cache_control(CacheControl::Medium)
        .fallback(Some("/index.html"))
        .fallback_status(axum::http::StatusCode::OK)
        .into_router();

    axum::Router::new()
        .route("/api/update", post(routes::v1::profile::update_profile))
        .route(
            "/api/profile/{username}/full",
            get(routes::v1::profile::get_profile_full),
        )
        .layer(middleware::from_fn_with_state(
            state.clone(),
            auth::jwt_middleware,
        ))
        .route("/api/report", post(routes::v1::report::report_url))
        .route("/api/auth/login", post(routes::v1::auth::login))
        .route("/api/auth/register", post(routes::v1::auth::register))
        .route("/api/auth/exchange", post(routes::v1::auth::exchange))
        .route(
            "/api/profile/{username}/preview",
            get(routes::v1::profile::get_profile_preview),
        )
        .with_state(state)
        .layer(TraceLayer::new_for_http())
        .layer(TimeoutLayer::new(Duration::from_secs(30)))
        .merge(memory_router)
}

pub async fn serve(flag: &str) {
    info!("Connecting to SQLite: db/linktea.db");
    let pool = SqlitePool::connect_with(
        SqliteConnectOptions::new()
            .filename("db/linktea.db")
            .create_if_missing(true),
    )
    .await
    .expect("Unable to connect with SQLite");

    info!("Running SQL migrations");
    sqlx::migrate!()
        .run(&pool)
        .await
        .expect("Unable to run database migrations");

    info!("Creating admin account if not already done");
    let moderator_password = match User::get_by_username(&pool, "moderator").await.unwrap() {
        None => {
            let pw = utils::generate_id(72);

            User::builder()
                .username("moderator")
                .bio("I moderate.")
                .password(&pw)
                .avatar_url("")
                .build()
                .insert(&pool)
                .await
                .expect("unable to create moderator account");

            pw
        }

        Some(u) => u.password,
    };

    info!("Configuring HTTP router");
    let routes = configure_router(&pool, flag, &moderator_password);

    info!("Starting HTTP server");
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3001").await.unwrap();

    info!("Listening on http://{}", listener.local_addr().unwrap());
    axum::serve(listener, routes)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .unwrap();
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    info!("Exit imminent")
}
