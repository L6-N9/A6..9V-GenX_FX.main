## 2024-07-22 - Non-blocking CPU-Bound Tasks in Asyncio

**Learning:** I discovered a performance bottleneck in `core/trading_engine.py` where a CPU-bound operation, `technical_indicators.add_all_indicators`, was blocking the `asyncio` event loop. Even though the I/O operations were concurrent, this synchronous calculation serialized the execution, negating the benefits of `asyncio.gather`.

**Action:** In the future, I will use `asyncio.to_thread` to run any CPU-bound function in a separate thread. This will keep the event loop free and ensure that both I/O and CPU-bound tasks can run in parallel, maximizing throughput.

## 2025-01-30 - Vectorizing Rolling Linear Regression Slope

**Learning:** I identified a major performance bottleneck in `utils/technical_indicators.py` where `rolling().apply(np.polyfit)` was used to calculate trend strength. This iterative approach is extremely slow because it invokes the SVD-based `polyfit` solver and Python-level overhead for every window.

**Action:** I replaced the iterative approach with a vectorized mathematical formula using `np.convolve` and `rolling().sum()`. This optimization provided a ~3x speedup for the `add_trend_indicators` method, significantly reducing the CPU load during market data processing and signal generation.

## 2025-01-30 - Row-wise Maximum and Arithmetic Overhead

**Learning:** I identified a significant performance bottleneck in the ADX calculation within `utils/technical_indicators.py`. Specifically, using `pd.concat([...], axis=1).max(axis=1)` to calculate the True Range (TR) is extremely inefficient compared to nested `np.maximum` calls. Additionally, performing row-wise arithmetic on Pandas Series carries substantial overhead for index alignment and validation.

**Action:** I replaced `pd.concat().max()` with nested `np.maximum` and moved arithmetic operations to raw NumPy arrays by using `.values`. This combination reduced the ADX calculation time by ~43%, demonstrating that bypassing the Pandas Series abstraction for simple row-wise math is a powerful optimization in hot code paths.

## 2025-02-12 - Reusing Intermediate Indicator Results

**Learning:** I identified a common performance anti-pattern where multiple technical indicators (e.g., Stochastic Oscillator, Williams %R, Bollinger Bands, and Support/Resistance) re-calculate the same rolling windows (min, max, mean, std) independently. This redundancy wastes CPU cycles, especially as the number of indicators grows.

**Action:** I refactored `utils/technical_indicators.py` to calculate shared rolling windows once and reuse them. For example, rolling min/max for window 14 is now shared between Stochastic and Williams %R, and `sma_20`/`std_20` are shared between Bollinger Bands and Volatility Indicators. This optimization provides a ~10-15% speedup across the affected methods without changing the output logic.

## 2025-05-15 - Vectorized Sliding Windows in Feature Engineering

**Learning:** I identified a massive performance bottleneck in `ai_models/feature_engineer.py` where Python loops were used to generate sliding windows for LSTMs and CNNs. Generating chart images was particularly slow (~1.7s for 2000 rows) due to repeated `.iloc` slicing and redundant normalization in every window. Additionally, the inference path redundantly calculated the entire history even though only the last window was needed.

**Action:** I replaced the Python loops with `numpy.lib.stride_tricks.sliding_window_view` for fully vectorized window generation, yielding a ~270x speedup for chart images. I also introduced an `only_last` flag to optimize the inference path, providing a ~60x speedup for real-time predictions. Using `np.stack` and `np.column_stack` on the vectorized windows ensures the multi-channel structure is maintained without explicit iteration.
