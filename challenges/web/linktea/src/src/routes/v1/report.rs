use crate::{routes::v1::ApiError, AppState};
use axum::{extract::State, Json};
use chromiumoxide::{Browser, BrowserConfig};
use futures::StreamExt;
use serde::Deserialize;
use std::{sync::Arc, time::Duration};
use tokio::sync::Semaphore;
use tracing::{debug, warn};

static BROWSER_PERMITS: Semaphore = Semaphore::const_new(1);

#[derive(Deserialize)]
pub struct ReportBody {
    path: String,
}

pub async fn report_url(
    State(state): State<Arc<AppState>>,
    Json(body): Json<ReportBody>,
) -> Result<(), ApiError> {
    if BROWSER_PERMITS.available_permits() == 0 {
        debug!("No browser permit available, preventing new report");
        return Err(ApiError::BrowserInUse);
    }
    let _permit = BROWSER_PERMITS.acquire().await.unwrap();
    debug!("Aquired browser permit");

    // PS: no_sandbox
    let (mut browser, mut handler) =
        Browser::launch(BrowserConfig::builder().no_sandbox().build().unwrap())
            .await
            .unwrap();

    let handle = tokio::spawn(async move {
        while let Some(h) = handler.next().await {
            if h.is_err() {
                warn!("Chromium handler received error: {:?}", h);
                break;
            }
        }

        warn!("Chromium handler loop exited");
    });

    debug!("Started Chromium handler loop");

    let base = "http://localhost:3001/".to_owned();
    let url = format!("{base}{}", body.path);
    debug!("Visiting {url}");

    let page = browser.new_page(url).await?;
    debug!("Waiting (4s)");
    tokio::time::sleep(Duration::from_secs(4)).await;

    if body.path.starts_with("idp/login") {
        debug!("Writing username into input");
        page.find_element("input[type=\"text\"]")
            .await?
            .click()
            .await?
            .type_str("moderator")
            .await?;

        debug!("Writing password into input");
        page.find_element("input[type=\"password\"]")
            .await?
            .click()
            .await?
            .type_str(state.moderator_secret.clone())
            .await?;

        debug!("Submitting login");
        page.find_element("button").await?.click().await?;

        debug!("Waiting (4s)");
        tokio::time::sleep(Duration::from_secs(4)).await;
    }

    debug!("Closing browser");
    browser.close().await?;
    browser.wait().await.unwrap();
    handle.await.unwrap();

    Ok(())
}
