# PREREG-C deviations

1. 2026-10-01T03:04Z launch: both l14 arms crashed at startup
   (KeyError 'beta_probe') — `tb.install()` replaces `tf.PINS` with
   tb's own dict, so the probe pin set on tf's dict at import never
   reached the resolver. No training step ran on either l14 arm; the
   o14 arms were unaffected and kept running. Fix: the pin now lives
   in `tb.PINS` (the surviving dict) as well; the guard's
   `test_leash_pins` now asserts both dicts post-plumbing. l14 arms
   relaunched with the same slots/seeds/band; relaunch timestamp in
   `results-raw/train-logs/l14-*.log`. No prediction, bar, or read
   changed.
