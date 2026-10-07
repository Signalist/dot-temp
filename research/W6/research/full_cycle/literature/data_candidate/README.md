# Bounded public output-length evidence

Source: Microsoft Azure / Microsoft Research, Azure LLM inference trace 2023 (conversation service).

- Official description: https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md
- Data: https://raw.githubusercontent.com/Azure/AzurePublicDataset/refs/heads/master/data/AzureLLMInferenceTrace_conv.csv
- Associated paper: Pratyush Patel, Esha Choukse, Chaojie Zhang, Aashaka Shah, Íñigo Goiri, Saeed Maleki, Ricardo Bianchini. Splitwise: Efficient generative LLM inference using phase splitting. ISCA 2024.
- License: Creative Commons Attribution 4.0 International; full official notice in AZURE_DATA_LICENSE.txt. Source data unchanged. The empirical PMF and summary are newly computed transformations.
- Retrieval: 2026-10-04, HTTP 200, 719,188 bytes, explicit two-megabyte read cap. Provenance/hash in retrieval.json.

Run `python prepare_empirical_lengths.py` to regenerate the PMF and summary from the retained CSV. Quantiles use the lower order statistic at floor(q*(n-1)). No rows removed. No external software or hardware command is needed.

The file has 19,366 rows, 623 distinct GeneratedTokens, mean 211.12594, median 129, p90 424, p99 601, support 7–1000. This is the entire official small conversation file, not a sampled prefix. It only spans the timestamps present in the file; it is not the full Azure population.

Important limitations:
1. The README reports collection on 2023-11-11, whereas retained timestamps run 2023-11-16 18:15:46.6805900 to 19:14:08.4025270. Do not silently choose one as proven actual acquisition time.
2. There is no completion reason or power trace. Natural EOS, output cap, cancellation and other termination cannot be separated.
3. ContextTokens spans 2–14050. Equating GeneratedTokens with identical work units is a modeling assumption, not measured constant token cost.
4. The empirical maximum 1000 defines this empirical PMF's support only; it is not a future hard upper bound.
5. Using the PMF in W6 is trace-driven synthetic work validation, not a controlled GPU service-curve or actuator-slew experiment.
