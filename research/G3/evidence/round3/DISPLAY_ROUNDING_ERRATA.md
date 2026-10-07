# Display-rounding errata / 展示舍入勘误

The frozen source document `G3_THIRD_ROUND_RESEARCH_DOSSIER_ZH.md` is preserved byte-for-byte for provenance. Its paragraph beginning “40位向外核验给出” contains three decimal displays that round upward while using the lower-bound sign “≥”. These three displayed inequalities therefore overstate the authoritative interval lower endpoint by their final digits.

冻结的中文源稿保留原样，不作改写。以下三处以“≥”表示的下界不应使用向上舍入的展示值；请使用保守向下截取值。权威数据是 `results/outward_zoh_inner.json` 中 `all_time_interval_lower_bounds` 的十进制下端点，换算展示单位时精确乘以 1000。

| Quantity | Frozen prose | Correct conservative display | Exact JSON lower endpoint after unit conversion |
|---|---:|---:|---:|
| 下 DC 余量 / lower DC slack | ≥ 1730.659214 J | ≥ 1730.659213 J | 1730.659213707814954248379369476471488276497763000 J |
| 命令余量 / command slack | ≥ 0.449999995 W | ≥ 0.449999994 W | 0.449999994840273327768305552952046648210275000 W |
| ramp 余量 / ramp slack | ≥ 29.999860 W/s | ≥ 29.999859 W/s | 29.999859853304268842214535163019264218158858000 W/s |

The exact interval JSON, certificate source, command payload, scientific replay and all positivity conclusions are unchanged. This is a prose-display correction only. It does not weaken or replace the stored outward interval certificate, change the physical contract, or add a hardware guarantee. The corresponding user-facing research report uses the conservative displays above.

精确区间 JSON、证书源码、命令载荷及复核结果均未改变；上述修正只涉及文字展示的舍入方向，不影响严格正余量结论。核验时以 JSON 的完整区间为准。
