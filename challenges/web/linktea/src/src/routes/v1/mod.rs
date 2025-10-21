use axum::{http::StatusCode, response::IntoResponse};
use core::fmt;
use serde::Serialize;
use std::fmt::Debug;
use tracing::warn;

pub mod auth;
pub mod profile;
pub mod report;

#[derive(Serialize)]
pub struct ApiErrorResponse {
    pub message: String,
    #[serde(rename = "errorKind")]
    pub kind: String,
}

#[derive(Debug)]
pub enum ApiError {
    NotFound,
    DatabaseError(sqlx::Error),
    MissingAuthentication,
    InvalidAuthentication,
    InvalidJwtSignature,
    JwtUserGone,
    ChromiumError,
    ValidationError,
    BrowserInUse,
    UsernameInUse,
    WrongPassword,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> axum::response::Response {
        let (status, message) = match &self {
            ApiError::NotFound => (StatusCode::NOT_FOUND, "Resource not found."),
            ApiError::DatabaseError(err) => {
				warn!("Database error occoured: {}", err);
				(StatusCode::INTERNAL_SERVER_ERROR, "Internal database error. Try again later.")
			},
            ApiError::MissingAuthentication => (
                StatusCode::UNAUTHORIZED,
                "Missing authentication. Supply a JWT in the cookie, or use a bearer in the `Authorization` header.",
            ),
			ApiError::InvalidAuthentication => (StatusCode::UNAUTHORIZED, "The supplied authentication is invalid."),
			ApiError::InvalidJwtSignature => (StatusCode::UNAUTHORIZED, "The supplied authentication has an invalid signature. Try logging in again."),
			ApiError::JwtUserGone => (StatusCode::UNAUTHORIZED, "Authenticated user does not exist. Has the account been deleted?"),
			ApiError::ChromiumError => (StatusCode::INTERNAL_SERVER_ERROR, "Report bot failure."),
			ApiError::ValidationError => (StatusCode::BAD_REQUEST, "Incorrect body data"),
            ApiError::BrowserInUse => (StatusCode::TOO_MANY_REQUESTS, "Report bot already active"),
            ApiError::UsernameInUse => (StatusCode::BAD_REQUEST, "Username already in use"),
            ApiError::WrongPassword => (StatusCode::BAD_REQUEST, "Incorrect username or password")
        };

        (
            status,
            axum::Json(ApiErrorResponse {
                message: message.to_string(),
                kind: self.kind(),
            }),
        )
            .into_response()
    }
}

// Get enum name to present in `type` field
impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        Debug::fmt(self, f)
    }
}

// Stupid way to get enum name without contents
impl ApiError {
    fn kind(&self) -> String {
        self.to_string()
            .split_once("(")
            .unwrap_or((self.to_string().as_str(), ""))
            .0
            .to_string()
    }
}

// Converting errors from other crates
impl From<sqlx::Error> for ApiError {
    fn from(value: sqlx::Error) -> Self {
        match value {
            sqlx::Error::RowNotFound => ApiError::NotFound,
            _ => ApiError::DatabaseError(value),
        }
    }
}

impl From<jsonwebtoken::errors::Error> for ApiError {
    fn from(value: jsonwebtoken::errors::Error) -> Self {
        match value.into_kind() {
            jsonwebtoken::errors::ErrorKind::ExpiredSignature
            | jsonwebtoken::errors::ErrorKind::InvalidSignature => ApiError::InvalidJwtSignature,
            _ => ApiError::InvalidAuthentication,
        }
    }
}

impl From<chromiumoxide::error::CdpError> for ApiError {
    fn from(e: chromiumoxide::error::CdpError) -> Self {
        warn!("Chromium Error: {:?}", e);
        ApiError::ChromiumError
    }
}

impl From<chromiumoxide::error::BrowserStderr> for ApiError {
    fn from(e: chromiumoxide::error::BrowserStderr) -> Self {
        warn!("Chromium Error: {:?}", e);
        ApiError::ChromiumError
    }
}

impl From<chromiumoxide::error::ChannelError> for ApiError {
    fn from(e: chromiumoxide::error::ChannelError) -> Self {
        warn!("Chromium Error: {:?}", e);
        ApiError::ChromiumError
    }
}

impl From<validator::ValidationErrors> for ApiError {
    fn from(_: validator::ValidationErrors) -> Self {
        ApiError::ValidationError
    }
}
