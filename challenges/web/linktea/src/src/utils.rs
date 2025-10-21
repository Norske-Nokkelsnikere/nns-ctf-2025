use rand::distr::{Alphanumeric, SampleString};
use rand::rngs::StdRng;
use rand::SeedableRng;

pub fn generate_id(len: usize) -> String {
    Alphanumeric.sample_string(&mut StdRng::from_rng(&mut rand::rng()), len)
}
