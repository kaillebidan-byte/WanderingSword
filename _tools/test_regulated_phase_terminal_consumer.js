"use strict";

const assert = require("assert");
const consumer = require("./regulated_phase_terminal_consumer.js");

function state(status, result) {
  const eventId = `quality-reaudit-${result}-terminal-001`;
  return {
    schema_version: 2,
    active_phase: "quality_reaudit",
    phases: {
      quality_reaudit: { status },
      narrative_readthrough: { status: "queued" }
    },
    signal_authorization: result ? {
      authorized: true,
      scope: "regulated_phase_terminal",
      phase_id: "quality_reaudit",
      result,
      event_id: eventId,
      evidence: ["_phase4_proofread/audit_status.json"]
    } : null,
    consumer_gate: {
      marker_only_accepted: false,
      live_state_match_required: true
    }
  };
}

const normal = consumer.validateRegulatedPhaseTerminal("train-23 merged\n", state("in_progress", null));
assert.strictEqual(normal.terminalCandidate, false);
assert.strictEqual(normal.accepted, false);
assert.deepStrictEqual(normal.errors, []);

const oldBad = consumer.validateRegulatedPhaseTerminal(
  "train-23 merged\n規定フェイズ完了\n",
  state("in_progress", null)
);
assert.strictEqual(oldBad.terminalCandidate, true);
assert.strictEqual(oldBad.accepted, false);
assert(oldBad.errors.some((error) => error.includes("not authorized")));

const twoLineBad = consumer.validateRegulatedPhaseTerminal(
  "規定フェイズ結果: success\n規定フェイズ完了\n",
  state("complete", "success")
);
assert.strictEqual(twoLineBad.accepted, false);
assert(twoLineBad.errors.some((error) => error.includes("authorization line")));

const inventedToken = consumer.validateRegulatedPhaseTerminal(
  "規定フェイズ認可: invented-event-999\n規定フェイズ結果: success\n規定フェイズ完了\n",
  state("complete", "success")
);
assert.strictEqual(inventedToken.accepted, false);

const successState = state("complete", "success");
const successId = successState.signal_authorization.event_id;
const valid = consumer.validateRegulatedPhaseTerminal(
  `フェイズ全体の根拠を確定した。\n規定フェイズ認可: ${successId}\n規定フェイズ結果: success\n規定フェイズ完了\n`,
  successState
);
assert.strictEqual(valid.accepted, true, valid.errors.join("; "));
assert.strictEqual(valid.result, "success");

const errorState = state("terminal_error", "error");
const errorId = errorState.signal_authorization.event_id;
const errorValid = consumer.validateRegulatedPhaseTerminal(
  `継続不能な終端エラー。\n規定フェイズ認可: ${errorId}\n規定フェイズ結果: error\n規定フェイズ完了\n`,
  errorState
);
assert.strictEqual(errorValid.accepted, true, errorValid.errors.join("; "));

console.log("test_regulated_phase_terminal_consumer: OK");
