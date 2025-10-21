use crate::utils;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;

#[derive(Serialize, Deserialize, Clone, Debug, sqlx::FromRow)]
pub struct Code {
    pub code: String,
    pub user_id: String,
}

#[bon::bon]
impl Code {
    #[builder]
    pub fn new(user_id: impl Into<String>) -> Code {
        Code {
            code: utils::generate_id(16),
            user_id: user_id.into(),
        }
    }

    pub async fn get(pool: &SqlitePool, code: String) -> Result<Option<Code>, sqlx::error::Error> {
        sqlx::query_as!(Code, "SELECT * FROM codes WHERE code = ?", code)
            .fetch_optional(pool)
            .await
    }

    pub async fn insert(&self, pool: &SqlitePool) -> Result<(), sqlx::error::Error> {
        sqlx::query!(
            "INSERT INTO codes (code, user_id) VALUES ($1, $2)",
            self.code,
            self.user_id,
        )
        .execute(pool)
        .await?;

        Ok(())
    }

    pub async fn delete(&self, pool: &SqlitePool) -> Result<(), sqlx::error::Error> {
        sqlx::query!("DELETE FROM codes WHERE code = ?", self.code)
            .execute(pool)
            .await?;

        Ok(())
    }
}
