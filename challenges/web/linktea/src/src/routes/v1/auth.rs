use crate::{
    auth,
    models::{code::Code, user::User},
    routes::v1::ApiError,
    AppState,
};
use axum::{extract::State, Json};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::sync::{Arc, LazyLock};
use validator::Validate;

static USERNAME_REGEX: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[a-zA-Z0-9_{}]*$").unwrap());

#[derive(Deserialize, Validate)]
pub struct LoginParams {
    #[validate(length(min = 1, max = 72), regex(path = *USERNAME_REGEX))]
    pub username: String,
    #[validate(length(min = 1))]
    pub password: String,
}

#[derive(Serialize)]
pub struct LoginResponse {
    pub code: String,
}

pub async fn login(
    State(state): State<Arc<AppState>>,
    Json(params): Json<LoginParams>,
) -> Result<Json<LoginResponse>, ApiError> {
    params.validate()?;

    let user = User::get_by_username(&state.db, &params.username)
        .await?
        .ok_or(ApiError::WrongPassword)?;

    if user.password != params.password {
        return Err(ApiError::WrongPassword);
    }

    let code = Code::builder().user_id(user.id).build();
    code.insert(&state.db).await?;
    Ok(Json(LoginResponse { code: code.code }))
}

pub async fn register(
    State(state): State<Arc<AppState>>,
    Json(params): Json<LoginParams>,
) -> Result<(), ApiError> {
    params.validate()?;

    if User::get_by_username(&state.db, &params.username)
        .await?
        .is_some()
    {
        return Err(ApiError::UsernameInUse);
    }

    let user = User::builder()
        .username(params.username)
        .password(params.password)
        .avatar_url("")
        .bio("A cool person")
        .build();

    user.insert(&state.db).await?;

    Ok(())
}

#[derive(Deserialize)]
pub struct ExchangeParams {
    pub code: String,
}

#[derive(Serialize)]
pub struct ExchangeResponse {
    pub jwt: String,
}

pub async fn exchange(
    State(state): State<Arc<AppState>>,
    Json(params): Json<ExchangeParams>,
) -> Result<Json<ExchangeResponse>, ApiError> {
    let code_query = Code::get(&state.db, params.code).await?;

    let code = code_query.ok_or(ApiError::NotFound)?;
    code.delete(&state.db).await?;
    let user = User::get_by_id(&state.db, &code.user_id).await?.unwrap();

    let jwt = auth::create_jwt(
        &user,
        &state.jwt_secret,
        if user.username == "moderator" {
            Some(&state.flag)
        } else {
            None
        },
    )
    .await;
    Ok(Json(ExchangeResponse { jwt }))
}
