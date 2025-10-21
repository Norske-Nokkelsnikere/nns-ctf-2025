use crate::{
    models::{self, user::User},
    routes::v1::ApiError,
    AppState,
};
use axum::{
    extract::{Request, State},
    http::header,
    middleware::Next,
    response::IntoResponse,
};
use axum_extra::extract::cookie::CookieJar;
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

#[derive(Serialize, Deserialize)]
pub struct TokenClaims {
    pub exp: usize,
    pub iat: usize,
    pub sub: String,
    pub username: String,
    pub flag: Option<String>,
}

pub async fn create_jwt(user: &User, secret: &str, flag: Option<&str>) -> String {
    let now = chrono::Utc::now();

    let claims = TokenClaims {
        iat: now.timestamp() as usize,
        exp: (now + chrono::Duration::hours(3)).timestamp() as usize,
        sub: user.id.clone(),
        username: user.username.clone(),
        flag: flag.map(|s| s.to_string()),
    };

    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret.as_ref()),
    )
    .unwrap()
}

pub async fn jwt_middleware(
    cookie_jar: CookieJar,
    State(data): State<Arc<AppState>>,
    mut req: Request,
    next: Next,
) -> Result<impl IntoResponse, ApiError> {
    let token = cookie_jar
        .get("linktea_jwt")
        .map(|cookie| cookie.value().to_string())
        .or_else(|| {
            req.headers()
                .get(header::AUTHORIZATION)
                .and_then(|auth_header| auth_header.to_str().ok())
                .and_then(|auth_value| auth_value.strip_prefix("Bearer "))
                .map(str::to_string)
        })
        .filter(|v| !v.trim().is_empty())
        .map(|v| v.trim().to_string());

    let token = token.ok_or(ApiError::MissingAuthentication)?;

    let claims = decode::<TokenClaims>(
        &token,
        &DecodingKey::from_secret(data.jwt_secret.as_ref()),
        &Validation::default(),
    )?
    .claims;

    let user = models::user::User::get_by_id(&data.db, &claims.sub).await?;
    let user = user.ok_or(ApiError::JwtUserGone)?;

    req.extensions_mut().insert(user);
    Ok(next.run(req).await)
}
