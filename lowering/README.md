<h1 align="center">🧬 Target-Language Lowering Examples</h1>

<p align="center">
  <b>How One CrypIR Slice Is Projected into Multiple Verifier-Facing Languages</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Source-CrypIR-blue">
  <img src="https://img.shields.io/badge/Examples-HLPSL%20%7C%20Maude%20%7C%20EC%20%7C%20CV-success">
  <img src="https://img.shields.io/badge/Purpose-Lowering%20Illustration-orange">
</p>

> These snippets illustrate the deterministic lowering step in CrypFormAgent. They are compact excerpts, not complete verifier scripts. The point is to show how a shared semantic object fixes roles, messages, and goals before model-assisted completion and verifier-guided repair.

---

## 🧩 Shared CrypIR Slice

| Element | Value |
| --- | --- |
| Roles | `A`, `B` |
| Message 1 | `A -> B : nonce` |
| Message 2 | `B -> A : enc_session_key_nonce` |
| Secrecy goal | preserve `session_key` secrecy |
| Authentication goal | authenticate the `enc_session_key_nonce` response |

---

## 🔐 HLPSL / AVISPA

```text
role_a / role_b
transition:
A sends Nonce
B receives Nonce
B sends EncSessionKeyNonce
A request(...)
goal:
secrecy_of session_key
authentication_on authentication_enc_session_key_nonce
```

---

## 🧮 Maude / Maude-NPA

```text
fmod NONCE-KEY-SYNTAX
ops: a, b, nonce, sessionkey, encsessionkeynonce
step-1: A -> B : nonce
step-2: B -> A : enc_session_key_nonce
search obligations:
secrecy(session_key)
authentication(enc_session_key_nonce)
```

---

## 🧪 EasyCrypt

```text
type agent.
type msg.
op nonce : msg.
op session_key : msg.
op enc_session_key_nonce : msg.

proc scheme()
lemma secrecy_session_key_secrecy
lemma authentication_enc_session_key_nonce_agreement
```

---

## 🛡️ CryptoVerif

```text
type cf_bitstring.
channel c.
query secret session_key.
query event(end_authentication(...))
  ==> event(begin_authentication(...)).

process ...
```

---

## 💡 Interpretation

Deterministic lowering gives the model a semantically grounded starting point:

| Lowering responsibility | Why it matters |
| --- | --- |
| Preserve roles and message order | Avoids role swaps and missing flows. |
| Preserve typed terms | Keeps nonce/key/ciphertext usage explicit. |
| Preserve goals | Ensures target verifier queries match the task label. |
| Preserve tool conventions | Reduces avoidable parse/type failures. |

CrypIR fixes the semantic anchors, while target-language scaffolds stabilize the shape of the artifact before model-assisted completion and verifier-guided repair.
