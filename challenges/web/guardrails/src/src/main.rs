use std::{env, sync::Arc};
use axum::{extract::State, routing::{get, post}, Json};
use bcrypt::DEFAULT_COST;
use tokio::sync::{mpsc, oneshot, Notify, RwLock};

#[tokio::main(worker_threads = 10)]
async fn main() {
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8000").await.expect("failed to bind");

    let secret_store = SecretStore::new();
    let state = Arc::new(AppState {secret_store: RwLock::new(secret_store)});

    let router = axum::Router::new()
        .route("/store", get(get_stored_secret).post(store_user_secret_in_store))
        .route("/store/flag", post(store_flag_in_store))
        .route("/store/check", post(check_stored_secret))
        .route("/store/protect", post(protect_store))
        .with_state(state);

    axum::serve(listener, router).await.expect("failed to serve");
}

struct AppState {
    secret_store: RwLock<SecretStore>
}

/// Stores the flag in the secret store and protects it from reading
async fn store_flag_in_store(State(state): State<Arc<AppState>>) {
    let secret_store = state.secret_store.write().await;
    let flag = env::var("FLAG").unwrap_or("-- flag only available in production --".to_string());
    secret_store.set_secret(flag).await;
    secret_store.protect_secret().await;
    println!("flag stored & protected");
}
/// Stores your secret in the store. Since your secrets aren't that valuable they aren't protected.
async fn store_user_secret_in_store(State(state): State<Arc<AppState>>, Json(secret): Json<String>,) {
    let secret_store = state.secret_store.write().await;
    secret_store.set_secret(secret).await;
    println!("store user secret");
}
/// Locks the current secret in the store from reading
async fn protect_store(State(state): State<Arc<AppState>>) {
    let secret_store = state.secret_store.write().await;
    secret_store.protect_secret().await;
    println!("protect user secret");
}
/// Retreives the stored secret.
/// This only gives a secret if one is stored, and if the stored secret is not protected.
async fn get_stored_secret(State(state): State<Arc<AppState>>) -> String {
    let secret_store = state.secret_store.read().await;
    let secret = secret_store.get_secret().await.unwrap_or("no public secret stored".to_string());
    println!("got stored secret");
    secret
}
/// Checks if the stored secret is what you provided.
/// This way you can check if you have the right secret :) 
async fn check_stored_secret(State(state): State<Arc<AppState>>, Json(expected): Json<String>) -> Json<bool> {
    let secret_store = state.secret_store.read().await;
    let is_valid = secret_store.check_secret(expected).await;

    Json(is_valid)
}

struct SecretStore {
    signal_tx: mpsc::UnboundedSender<SignalRequest>
}
impl SecretStore {
    pub fn new() -> Self {
        let (signal_tx, signal_rx) = mpsc::unbounded_channel();
        tokio::spawn(Self::management_task(signal_rx));
        Self {
            signal_tx
        }
    }
    pub async fn set_secret(&self, secret: String) {
        let processed_notifier = Arc::new(Notify::new());
        self.signal_tx.send(SignalRequest::SetSecret(SetSecretRequest { secret, processed_notifier: processed_notifier.clone() })).expect("signal channel closed");
        processed_notifier.notified().await;
    }
    pub async fn protect_secret(&self) {
        let processed_notifier = Arc::new(Notify::new());
        self.signal_tx.send(SignalRequest::ProtectSecret(ProtectSecretRequest { processed_notifier: processed_notifier.clone() })).expect("signal channel closed");
        processed_notifier.notified().await;
    }
    pub async fn get_secret(&self) -> Option<String> {
        let (response_tx, response_rx) = oneshot::channel();
        self.signal_tx.send(SignalRequest::GetSecret(GetSecretRequest { response_tx })).expect("signal channel closed");
        response_rx.await.expect("response channel closed without response")
    }
    pub async fn check_secret(&self, expected: String) -> bool {
        let (response_tx, response_rx) = oneshot::channel();
        self.signal_tx.send(SignalRequest::CheckSecret(CheckSecretRequest { response_tx, expected })).expect("signal channel closed");
        response_rx.await.expect("response channel closed without response")
    }
    async fn management_task(mut signal_rx: mpsc::UnboundedReceiver<SignalRequest>) {
        let mut secret: Option<StoredSecret> = None;
        loop {
            let Some(response) = signal_rx.recv().await else {
                return;
            };
            match response {
                SignalRequest::GetSecret(request) => {
                    let Some(ref secret) = secret else {
                        let _ = request.response_tx.send(None);
                        continue
                    };
                    if secret.protected {
                        let _ = request.response_tx.send(None);
                    } else {
                        let _ = request.response_tx.send(Some(secret.plaintext.clone()));
                    }
                },
                SignalRequest::SetSecret(request) => {
                    let secret_hash = bcrypt::hash(request.secret.as_bytes(), DEFAULT_COST).expect("failed to hash secret");
                    secret = Some(StoredSecret {
                        plaintext: request.secret.clone(),
                        hashed: secret_hash,
                        protected: false
                    });
                    request.processed_notifier.notify_waiters();
                },
                SignalRequest::ProtectSecret(request) => {
                    if let Some(ref mut secret) = secret {
                        secret.protected = true;
                    }
                    request.processed_notifier.notify_waiters();
                },
                SignalRequest::CheckSecret(request) => {
                    let Some(secret) = &secret else {
                        continue;
                    };
                    let is_valid = bcrypt::verify(request.expected.as_bytes(),&secret.hashed).unwrap_or(false);

                    let _ = request.response_tx.send(is_valid);

                }
            }
            
        }
    }
}

enum SignalRequest {
    SetSecret(SetSecretRequest),
    ProtectSecret(ProtectSecretRequest),
    GetSecret(GetSecretRequest),
    CheckSecret(CheckSecretRequest)
}
struct ProtectSecretRequest {
    processed_notifier: Arc<Notify>
}
struct SetSecretRequest {
    secret: String,
    processed_notifier: Arc<Notify>
}
struct GetSecretRequest {
    response_tx: oneshot::Sender<Option<String>>
}
struct CheckSecretRequest {
    expected: String,
    response_tx: oneshot::Sender<bool>
}
struct StoredSecret {
    pub plaintext: String,
    pub hashed: String,
    pub protected: bool
}
