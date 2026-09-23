# FrameBridge Community Introduction Draft — 2026-09-23

Status: ready for channel selection and posting; **not yet posted**

The signed-in Discord browser could not be inspected on 2026-09-23 because the browser-control inventory repeatedly returned a request-header-policy error. Do not infer a channel, claim a post exists, or submit this draft blindly. Check the channel rules and neighboring posts when browser access returns.

## Suggested Discord post

> I’ve just open-sourced **Ashleaf** and its first tool, **FrameBridge**—a coordinate-safe, sparse validation layer for Vesuvius winding experiments: <https://github.com/stanleyngugi/ashleaf>
>
> The vision is a trust layer between candidate geometry and virtual unwrapping: before a winding constraint reaches a fitter, we should know its coordinate frame, whether the underlying CT-derived field actually supports the estimator rays, and whether that estimator is operating in a regime where its output is credible.
>
> The first release makes the Paris 4 2.4 µm→9.6 µm frame contract explicit (credit to the earlier `constraint-gauge` correction), validates sparse `respool` indexes and exact HTTP byte-range plans, and publishes negative controls plus per-mesh failure analysis for frozen E1. The CPU-only public-data demo fetches ~4 MiB of pinned metadata and produces a one-mesh range plan without downloading CT payload: [quickstart](https://github.com/stanleyngugi/ashleaf/blob/main/docs/32_framebridge_public_demo.md).
>
> One important scope note: the current local adjacent-wrap diagnostic contains only constructed `dw=+1` targets. Its reported E1 agreement is **not** a gain over the 100%-accurate constant-`+1` label baseline, nor a production constraint/fitter result. The useful result today is that the system surfaces where frame/support/applicability assumptions break, including large cross-segment variation in E1 agreement.
>
> I’d especially value someone independently running the quickstart or trying the frame contract on another verified mesh, and telling me where the interface or assumptions fail. Next up are mixed-label candidate evaluation, registration/parity checks, and reason-coded output into spiral fitting. The repo includes full protocols, failed experiments, tests, and a detailed prepublication audit. Developed with substantial OpenAI Codex assistance under my direction; numerical claims are tied to the recorded evidence.

## Posting discipline

1. Confirm the relevant channel permits project announcements and GitHub links.
2. Check whether a shorter post or dedicated thread is expected there.
3. Post the link and ask for one specific reproduction or critique; do not imply official endorsement or a submitted prize entry.
4. Record the post URL, date, channel, feedback, and any resulting changes in this document.
5. If a community member reports a counterexample, preserve the initial claim and record the correction rather than silently rewriting history.
