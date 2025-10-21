use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;

use crate::utils;

#[derive(Serialize, Deserialize, Clone, Debug, sqlx::FromRow)]
pub struct User {
    pub id: String,
    pub username: String,
    pub password: String,
    pub avatar_url: String,
    pub bio: String,
}

#[bon::bon]
impl User {
    #[builder]
    pub fn new(
        username: impl Into<String>,
        password: impl Into<String>,
        avatar_url: impl Into<String>,
        bio: impl Into<String>,
    ) -> User {
        User {
            id: utils::generate_id(8),
            username: username.into(),
            password: password.into(),
            avatar_url: avatar_url.into(),
            bio: bio.into(),
        }
    }

    pub async fn get_by_id(
        pool: &SqlitePool,
        id: &str,
    ) -> Result<Option<User>, sqlx::error::Error> {
        sqlx::query_as!(User, "SELECT * FROM users WHERE id = ?", id)
            .fetch_optional(pool)
            .await
    }

    pub async fn get_by_username(
        pool: &SqlitePool,
        username: &str,
    ) -> Result<Option<User>, sqlx::error::Error> {
        sqlx::query_as!(User, "SELECT * FROM users WHERE username = ?", username)
            .fetch_optional(pool)
            .await
    }

    pub async fn insert(&self, pool: &SqlitePool) -> Result<(), sqlx::error::Error> {
        sqlx::query!(
            "INSERT INTO users (id, username, password, avatar_url, bio) VALUES ($1, $2, $3, $4, $5)",
            self.id,
            self.username,
            self.password,
            self.avatar_url,
            self.bio,
        )
        .execute(pool)
        .await?;

        Ok(())
    }

    pub async fn update(
        &mut self,
        pool: &SqlitePool,
        new_bio: Option<String>,
        new_avatar_url: Option<String>,
    ) -> Result<(), sqlx::error::Error> {
        let mut tx = pool.begin().await?;

        if let Some(bio) = new_bio {
            sqlx::query!("UPDATE users SET bio = $2 WHERE id = $1", self.id, bio)
                .execute(&mut *tx)
                .await?;

            self.bio = bio.to_string();
        }

        if let Some(avatar_url) = new_avatar_url {
            sqlx::query!(
                "UPDATE users SET avatar_url = $2 WHERE id = $1",
                self.id,
                avatar_url
            )
            .execute(&mut *tx)
            .await?;

            self.avatar_url = avatar_url.to_string();
        }

        tx.commit().await?;
        Ok(())
    }
}
