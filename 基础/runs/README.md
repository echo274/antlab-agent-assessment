# 基础题运行记录分组清单（runs/）

本目录 67 个 `<run_id>.json` 由 `基础/starter/runner.py` 落盘，每条记录含输入 messages、原始响应、usage、客户端耗时、`data_sha256`、`student_sha256`、配置 hash 等。其中 40 个进入判分（`results/results.csv`），其余为开发调试、重试与诊断探索；原始失败均保留、不被最终结果覆盖。

## 分组总览

| 分组 | 数量 | 进入 results.csv | 说明 |
|---|---|---|---|
| 主实验·基线首次 | 32 | ✅ | T01–T08 × R0/R1/R2/K，deepseek-chat（14:52 批次） |
| 主实验·改进首次 | 8 | ✅ | T01–T08 × R0 improved，deepseek-chat（14:53 批次） |
| 基线重试 | 2 | ❌ | T01 R0 的两次重试（15:05 / 15:08），未覆盖首次 |
| 开发题调试 | 20 | ❌ | D01–D04 的 E/R0/K 调试（含 dry/mock/paid） |
| reasoner 探索 | 4 | ❌ | T01/T04/T07/T08 R0，deepseek-reasoner（诊断对照） |
| pro 探索 | 1 | ❌ | T01 R0，deepseek-pro（一次探索） |

判分脚本 `results/scoring/score.py` 离线复算这 40 个主实验并生成 `results/results.csv`；诊断/变体检查见 `results/checks/checks.py`。

## 1. 主实验·基线首次（32，进判分）

| run_id | case | cond | model | 时间(UTC) |
|---|---|---|---|---|
| e378bccd-5350-4262-a0a2-eda10177bfb2 | T01 | K | deepseek-chat | 14:52:11 |
| d7b637d9-54a6-458d-8ad1-cc6bf4e88dcc | T01 | R0 | deepseek-chat | 14:52:10 |
| 33580b91-6c7f-4b2d-999a-f145d74e5780 | T01 | R1 | deepseek-chat | 14:52:12 |
| f1f0eb50-6e5e-4d1b-9cac-b4477a20ee41 | T01 | R2 | deepseek-chat | 14:52:20 |
| fc55488e-9d25-46cf-a757-99ad1426a541 | T02 | K | deepseek-chat | 14:52:15 |
| 6c49b53b-2bd2-4ee7-bdfb-dfa0e7f30b49 | T02 | R0 | deepseek-chat | 14:52:07 |
| f4522250-48c9-4abd-b6f2-ad567b3ff414 | T02 | R1 | deepseek-chat | 14:52:05 |
| 6f4ebd65-582b-480f-a513-898c1698f7a0 | T02 | R2 | deepseek-chat | 14:52:16 |
| 53ab5a6b-d2af-4eb9-a94d-016e9010d9b5 | T03 | K | deepseek-chat | 14:52:07 |
| ace2480a-c63f-4422-b4b7-1d4258f1e462 | T03 | R0 | deepseek-chat | 14:52:02 |
| 1157ff90-a908-4668-9e6a-9f20e9649181 | T03 | R1 | deepseek-chat | 14:52:18 |
| c008202a-6422-4972-a8d0-f7eb0e742724 | T03 | R2 | deepseek-chat | 14:52:03 |
| 97e2594a-858b-4817-a266-42b551f2d1aa | T04 | K | deepseek-chat | 14:52:07 |
| e7f0bf1a-9f36-4d31-8c9b-a60cd76c7484 | T04 | R0 | deepseek-chat | 14:52:01 |
| 13bbfd48-a3de-432e-94cf-38e696695c2d | T04 | R1 | deepseek-chat | 14:52:04 |
| fe0fabd3-bbc2-401c-9636-9c1ea8799d69 | T04 | R2 | deepseek-chat | 14:52:08 |
| 123b616c-3eb3-43cb-9f5a-8ba7c375d533 | T05 | K | deepseek-chat | 14:52:02 |
| 84c0a92f-db25-4444-af62-6f9f26e7a343 | T05 | R0 | deepseek-chat | 14:52:17 |
| 49f9966e-68fd-4565-93ef-c520ee3815f1 | T05 | R1 | deepseek-chat | 14:52:15 |
| fd30354d-f1cd-4096-a83e-e7700abc3fd2 | T05 | R2 | deepseek-chat | 14:52:09 |
| 78023b77-2eae-47e5-b12b-f1b505103e0a | T06 | K | deepseek-chat | 14:52:10 |
| 5fb3b071-9ad9-4116-8360-448e0be51c4a | T06 | R0 | deepseek-chat | 14:52:14 |
| 3acb9fd0-93ed-417f-a86c-0ce3e73f5327 | T06 | R1 | deepseek-chat | 14:52:19 |
| c4bd9b46-d214-4cd1-9e6e-8a2e8a1e6b64 | T06 | R2 | deepseek-chat | 14:52:13 |
| a73283b7-3505-4008-9f06-2f0ba88a749b | T07 | K | deepseek-chat | 14:52:06 |
| b9ee6511-92ae-4fb3-a572-7ebb5e564ca9 | T07 | R0 | deepseek-chat | 14:52:13 |
| 092a9c12-7a31-4b99-bc62-3ba7ac023e97 | T07 | R1 | deepseek-chat | 14:52:05 |
| a3dc2ccc-f554-49ba-8133-cab8e0ea330b | T07 | R2 | deepseek-chat | 14:52:14 |
| 350d260c-c26e-43a9-a895-b62b572d5a45 | T08 | K | deepseek-chat | 14:52:21 |
| 78906213-13b5-4f80-a4ea-89ec4a4d7e81 | T08 | R0 | deepseek-chat | 14:52:18 |
| 87f6cf07-2087-4a07-8d8c-1168185d9be6 | T08 | R1 | deepseek-chat | 14:52:03 |
| 25df9aad-fcaa-449d-bb5a-49540c4f0264 | T08 | R2 | deepseek-chat | 14:52:00 |

## 2. 主实验·改进首次（8，进判分）

| run_id | case | cond | model | 时间(UTC) |
|---|---|---|---|---|
| 526f48fc-736f-46ff-bdc7-345068b51ce6 | T01 | R0 | deepseek-chat | 14:53:23 |
| c36009bd-ec9c-431e-8147-106fd53a0d8f | T02 | R0 | deepseek-chat | 14:53:18 |
| 5694e677-c0f9-4dfc-b920-e2cfb2879498 | T03 | R0 | deepseek-chat | 14:53:21 |
| 828adaac-ef99-46ea-b4d7-2aea024e9838 | T04 | R0 | deepseek-chat | 14:53:19 |
| b5960547-5fce-4808-8297-f08312ef1ca3 | T05 | R0 | deepseek-chat | 14:53:20 |
| 2162e431-e46d-4e0e-b154-afb833154283 | T06 | R0 | deepseek-chat | 14:53:22 |
| 4df0e228-088e-43fe-9477-a9931d4e6d8a | T07 | R0 | deepseek-chat | 14:53:18 |
| 9e752437-7a21-43ec-8dc6-42293eeefcb7 | T08 | R0 | deepseek-chat | 14:53:23 |

## 3. 基线重试（2，未进判分）

T01 R0 主实验首跑后为确认「套规则失败」结论，又重跑了两次；判分以首次 `d7b637d9` 为准，以下两次仅作佐证、不覆盖首次。

| run_id | case | cond | model | 时间(UTC) |
|---|---|---|---|---|
| 7516e440-7f99-477e-bcc0-360403cb5ed3 | T01 | R0 | deepseek-chat | 15:05:15 |
| a4df9de8-5aa1-4552-a100-561ab5c26f1d | T01 | R0 | deepseek-chat | 15:08:01 |

## 4. 开发题调试（20，未进判分）

D01–D04 开发题（E/R0/K 条件）的调参/调试运行，含 dry（不调模型）、mock（假响应）与 paid（真实调用）。开发题答案不进正式模型输入，仅用于验证实现。

| run_id | case | cond | variant | mode | model |
|---|---|---|---|---|---|
| 1e301583-74af-4d1e-9efd-a282f95341a7 | D01 | E | baseline | dry | deepseek-chat |
| 3b2da4c4-20d0-4224-b1ba-493113cf055c | D01 | E | baseline | mock | deepseek-chat |
| 26649310-2f9c-4f8b-b02e-9682c9f09b4f | D01 | E | baseline | paid | deepseek-chat |
| 86acc4d1-6e63-45fb-aec6-09b0e0d610ab | D01 | E | baseline | paid | deepseek-chat |
| b657c4b8-3ba2-4ffa-a1e3-5e90ba8d1406 | D01 | K | baseline | paid | deepseek-chat |
| 66846ccf-7742-4f05-a6fd-95f577d43b80 | D01 | R0 | baseline | paid | deepseek-chat |
| 06a70bec-93f9-404b-ac89-edead65e0185 | D01 | R0 | improved | dry | deepseek-chat |
| 2e594c8d-1d29-44e4-9876-aa0743f134ab | D01 | R0 | improved | paid | deepseek-chat |
| 53cc9318-26bd-4e07-8c37-2abbc8435576 | D02 | E | baseline | paid | deepseek-chat |
| 614ca366-7e7b-4845-897b-f626cd3f42ef | D02 | K | baseline | paid | deepseek-chat |
| a9ee0ec5-6d2f-4b27-ac8a-3e6faf2c4b91 | D02 | R0 | baseline | paid | deepseek-chat |
| c777c717-40e6-4593-9dfc-b8b67217f669 | D02 | R0 | improved | paid | deepseek-chat |
| 9743c58d-5cd4-4f94-bb2a-268720b4fbe2 | D03 | E | baseline | paid | deepseek-chat |
| 9947f4d2-3568-4a35-bfca-dd3284ce513f | D03 | K | baseline | paid | deepseek-chat |
| 17bee7f0-4c61-4cea-877f-88e11ec6c55a | D03 | R0 | baseline | paid | deepseek-chat |
| 286b671c-979d-4b8a-ba6d-67d2322d877e | D03 | R0 | improved | paid | deepseek-chat |
| c94aa78b-fd46-4821-861b-0a7f443e8e4a | D04 | E | baseline | paid | deepseek-chat |
| b0617037-ce6c-429d-bb47-4e161e12ceb8 | D04 | K | baseline | paid | deepseek-chat |
| bfb62404-2dd7-4028-80fb-f10c4fccfe36 | D04 | R0 | baseline | paid | deepseek-chat |
| 351bf7f6-6bf8-417e-8140-2bdf2eb5dd8e | D04 | R0 | improved | paid | deepseek-chat |

## 5. reasoner 探索（4，未进判分）

用 `deepseek-reasoner`（推理模型）重跑套规则失败题 T01/T04/T07/T08 的 R0 基线，作诊断对照：证明失败来自模型推理强度而非证据组织方法（详见 `report.md` 第 2/5 节、`results/checks/checks.py`）。

| run_id | case | cond | model |
|---|---|---|---|
| f9477ccd-8834-4961-a585-5c3430200426 | T01 | R0 | deepseek-reasoner |
| 97212e1f-75de-468f-af4a-9fd61356c521 | T04 | R0 | deepseek-reasoner |
| 60790b51-e02a-4e76-a429-b20995de4f7d | T07 | R0 | deepseek-reasoner |
| 11931b6f-188a-4992-b6b8-09fcf2c83ed6 | T08 | R0 | deepseek-reasoner |

## 6. pro 探索（1，未进判分）

| run_id | case | cond | model |
|---|---|---|---|
| df2aac03-65c6-4804-bfe0-71284c2994a8 | T01 | R0 | deepseek-pro |
