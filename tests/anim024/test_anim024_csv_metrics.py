"""Regression gates for UE5.7 CSVProfiler numeric evidence.

A command line containing -fpschart/-csvprofile is not proof of measurement.
Accept valid per-frame samples only, and reject UE's repeated header/metadata rows.
"""
import math
import unittest
from tools.assetforge.anim024_ue_csv_benchmark import summarize_csv_text

CSV = (
    "EVENTS,FrameTime,GameThreadTime,RenderThreadTime,GPUTime,GPUMem/LocalUsedMB,View/Speed\n"
    ",20,3,12,9,600,0\n"
    ",5,2,4,3,700,0\n"
    ",7,2.2,6,4,710,0\n"
    "EVENTS,FrameTime,GameThreadTime,RenderThreadTime,GPUTime,GPUMem/LocalUsedMB,View/Speed\n"
    "[HasHeaderRowAtEnd],1,[rhiname],D3D12,[enginereleaseversion],5.7.4\n"
)


class CsvProfilerNumericEvidence(unittest.TestCase):
    def test_repeated_headers_and_metadata_do_not_count_as_frames(self):
        r = summarize_csv_text(CSV, warmup_frames=1)
        self.assertEqual(r["frame_count"], 3)
        self.assertEqual(r["warm_frame_count"], 2)
        self.assertEqual(r["warm"]["frame_time_ms"]["mean"], 6.0)
        self.assertAlmostEqual(r["warm"]["fps_from_mean_frame_time"], 166.666667, places=4)
        self.assertEqual(r["warm"]["gpu_time_ms"]["mean"], 3.5)
        self.assertEqual(r["warm"]["gpu_memory_used_mb"]["max"], 710.0)

    def test_does_not_confuse_benchmark_capture_with_real_gameplay(self):
        r = summarize_csv_text(CSV, warmup_frames=1)
        self.assertFalse(r["gameplay_fps_certified"])
        self.assertFalse(r["before_after_delta_certified"])
        self.assertEqual(r["scope"], "UE CSV sample statistics only")

    def test_rejects_missing_numeric_frame_columns(self):
        with self.assertRaises(ValueError):
            summarize_csv_text("EVENTS,FrameTime\n,6\n")

    def test_rejects_empty_or_nonfinite_or_zero_frame_times(self):
        for bad in ("EVENTS,FrameTime,GPUTime\n", "EVENTS,FrameTime,GPUTime\n,0,3\n",
                    "EVENTS,FrameTime,GPUTime\n,nan,3\n",
                    "EVENTS,FrameTime,GPUTime\n,inf,3\n"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    summarize_csv_text(bad)

    def test_rejects_warmup_equal_to_entire_sample(self):
        with self.assertRaises(ValueError):
            summarize_csv_text(CSV, warmup_frames=3)

    def test_p99_is_frame_time_not_instantaneous_fps_percentile(self):
        r = summarize_csv_text(CSV, warmup_frames=0)
        self.assertGreater(r["all"]["frame_time_ms"]["p99"], 19)
        self.assertLess(r["all"]["fps_from_mean_frame_time"], 100)

    def test_zero_warmup_permits_one_sample(self):
        r = summarize_csv_text("EVENTS,FrameTime,GPUTime\n,10,9\n", warmup_frames=0)
        self.assertEqual(r["all"]["fps_from_mean_frame_time"], 100.0)

    def test_non_numeric_gpu_sample_rejected(self):
        with self.assertRaises(ValueError):
            summarize_csv_text("EVENTS,FrameTime,GPUTime\n,10,fail\n")

    def test_negative_warmup_rejected(self):
        with self.assertRaises(ValueError):
            summarize_csv_text(CSV, warmup_frames=-1)


if __name__ == "__main__":
    unittest.main()
