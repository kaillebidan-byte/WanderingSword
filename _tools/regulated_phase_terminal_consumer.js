/* eslint-disable no-var */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  if (root) {
    root.WanderingSwordPhaseTerminal = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var MARKER = "規定フェイズ完了";
  var AUTH_PREFIX = "規定フェイズ認可: ";
  var STATUS_PREFIX = "規定フェイズ結果: ";
  var VALID_RESULTS = new Set(["success", "error"]);
  var EVENT_ID_RE = /^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$/;

  function linesOf(text) {
    return String(text || "")
      .split(/\r?\n/)
      .map(function (line) { return line.replace(/\s+$/, ""); })
      .filter(function (line) { return line.trim().length > 0; });
  }

  function validateRegulatedPhaseTerminal(responseText, state) {
    var lines = linesOf(responseText);
    var markerCount = lines.filter(function (line) { return line === MARKER; }).length;
    var candidate = markerCount > 0;
    var errors = [];

    if (!candidate) {
      return {
        accepted: false,
        terminalCandidate: false,
        result: null,
        phaseId: null,
        eventId: null,
        errors: []
      };
    }

    if (markerCount !== 1) {
      errors.push("reserved marker must occur exactly once");
    }
    if (lines[lines.length - 1] !== MARKER) {
      errors.push("reserved marker must be the last non-empty line");
    }

    var authorization = state && state.signal_authorization;
    var gate = state && state.consumer_gate;
    if (!gate || gate.marker_only_accepted !== false || gate.live_state_match_required !== true) {
      errors.push("live consumer gate is missing or permissive");
    }
    if (!authorization || authorization.authorized !== true) {
      errors.push("terminal signal is not authorized in live state");
    }

    var resultLine = lines.length >= 2 ? lines[lines.length - 2] : "";
    var authLine = lines.length >= 3 ? lines[lines.length - 3] : "";
    var result = resultLine.indexOf(STATUS_PREFIX) === 0
      ? resultLine.slice(STATUS_PREFIX.length)
      : null;
    if (!VALID_RESULTS.has(result)) {
      errors.push("valid result line must immediately precede marker");
    }

    var eventId = authorization && typeof authorization.event_id === "string"
      ? authorization.event_id
      : null;
    if (!eventId || !EVENT_ID_RE.test(eventId)) {
      errors.push("live authorization event ID is invalid");
    }
    if (!eventId || authLine !== AUTH_PREFIX + eventId) {
      errors.push("authorization line must match the live event ID");
    }

    var phaseId = authorization && authorization.phase_id;
    if (!state || phaseId !== state.active_phase) {
      errors.push("authorization phase does not match active phase");
    }
    if (!authorization || authorization.scope !== "regulated_phase_terminal") {
      errors.push("authorization scope mismatch");
    }
    if (!authorization || authorization.result !== result) {
      errors.push("authorization result mismatch");
    }

    var phases = state && state.phases;
    var phase = phases && phaseId ? phases[phaseId] : null;
    var expectedStatus = result === "success" ? "complete" : "terminal_error";
    if (!phase || phase.status !== expectedStatus) {
      errors.push("active phase is not in the required terminal status");
    }

    return {
      accepted: errors.length === 0,
      terminalCandidate: true,
      result: result,
      phaseId: phaseId || null,
      eventId: eventId,
      errors: errors
    };
  }

  return {
    MARKER: MARKER,
    AUTH_PREFIX: AUTH_PREFIX,
    STATUS_PREFIX: STATUS_PREFIX,
    validateRegulatedPhaseTerminal: validateRegulatedPhaseTerminal
  };
});
