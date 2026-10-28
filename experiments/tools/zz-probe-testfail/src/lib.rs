pub fn add(a: u32, b: u32) -> u32 {
    a + b
}

#[cfg(test)]
mod tests {
    #[test]
    fn probe_fails() {
        assert_eq!(super::add(1, 1), 3);
    }
}
