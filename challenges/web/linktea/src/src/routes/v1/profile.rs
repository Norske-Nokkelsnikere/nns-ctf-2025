use std::sync::Arc;

use crate::{models::user::User, routes::v1::ApiError, AppState};
use axum::{
    extract::{Path, State},
    Extension, Json,
};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct ProfileParams {
    username: String,
}

#[derive(Serialize)]
pub struct ProfilePreviewResponse {
    avatar_url: String,
}

pub async fn get_profile_preview(
    State(state): State<Arc<AppState>>,
    Path(params): Path<ProfileParams>,
) -> Result<Json<ProfilePreviewResponse>, ApiError> {
    let user = User::get_by_username(&state.db, &params.username)
        .await?
        .ok_or(ApiError::NotFound)?;

    Ok(Json(ProfilePreviewResponse {
        avatar_url: user.avatar_url,
    }))
}

pub async fn get_profile_full(
    State(state): State<Arc<AppState>>,
    Path(params): Path<ProfileParams>,
) -> Result<Json<User>, ApiError> {
    let user = User::get_by_username(&state.db, &params.username)
        .await?
        .ok_or(ApiError::NotFound)?;

    Ok(Json(user))
}

#[derive(Deserialize)]
pub struct ProfileUpdateBody {
    avatar_url: Option<String>,
    bio: Option<String>,
}

pub async fn update_profile(
    State(state): State<Arc<AppState>>,
    Extension(authenticated_user): Extension<User>,
    Json(params): Json<ProfileUpdateBody>,
) -> Result<Json<User>, ApiError> {
    let mut user = User::get_by_id(&state.db, &authenticated_user.id)
        .await?
        .ok_or(ApiError::NotFound)?;

    if let Some(avatar) = params.avatar_url.clone() {
        if !avatar.starts_with("http://") && !avatar.starts_with("https://") {
            return Err(ApiError::ValidationError);
        }
    }

    user.update(&state.db, params.bio, params.avatar_url)
        .await?;

    Ok(Json(user))
}
