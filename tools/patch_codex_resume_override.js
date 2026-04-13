#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const TARGET_CONVERSATION_ID =
  "019c0a5e-4c63-7fb1-9dc8-2afc401b57bd";
const DEFAULT_JS_PATH =
  "/Users/jamison/.antigravity/extensions/openai.chatgpt-26.406.31014-darwin-x64/webview/assets/app-server-manager-hooks-pp-5w9Ur.js";
const BACKUP_ROOT =
  process.env.CODEX_PATCH_BACKUP_ROOT ||
  "/Users/jamison/.antigravity/rollback_backups";
const PATCH_TAG = "maybe_resume_local_override";

const targetPath = process.argv[2] || DEFAULT_JS_PATH;

const insertionAnchor =
  "let m=c?.turns.at(-1)?.params,h=ae(d),g=o?.approvalsReviewer??m?.approvalsReviewer??`user`,_=o??{approvalPolicy:m?.approvalPolicy??h.approvalPolicy,approvalsReviewer:g,sandboxPolicy:m?.sandboxPolicy??h.sandboxPolicy},v=n??c?.latestCollaborationMode.settings.model??s?.settings.model??null,y=await e.buildNewConversationParams(v,r===void 0?e.getEffectiveServiceTier(Do()):r,d[0]??`/`,_,_.approvalsReviewer,{threadId:t}),b=await e.sendRequest(`thread/resume`,";

const replacement =
  "let m=c?.turns.at(-1)?.params,h=ae(d),g=o?.approvalsReviewer??m?.approvalsReviewer??`user`,_=o??{approvalPolicy:m?.approvalPolicy??h.approvalPolicy,approvalsReviewer:g,sandboxPolicy:m?.sandboxPolicy??h.sandboxPolicy},v=n??c?.latestCollaborationMode.settings.model??s?.settings.model??null;if(t===`" +
  TARGET_CONVERSATION_ID +
  "`&&p!=null){e.updateConversationState(t,e=>{e.resumeState=`resumed`,e.latestModel=v??e.latestModel,e.latestReasoningEffort=i??e.latestReasoningEffort,e.latestCollaborationMode={mode:`default`,settings:{...s?.settings,model:v??e.latestModel,reasoning_effort:i??e.latestReasoningEffort,developer_instructions:null}}});let O=f.at(-1)??null;e.markConversationStreaming(t),e.setConversationStreamRole(t,{role:`owner`}),e.broadcastConversationSnapshot(t),F.warning(`" +
  PATCH_TAG +
  "`,{safe:{conversationId:t,turnCount:f.length,latestTurnId:O?.turnId??null,reason:`skip_live_resume_for_corrupt_remote_state`},sensitive:{}});return}let y=await e.buildNewConversationParams(v,r===void 0?e.getEffectiveServiceTier(Do()):r,d[0]??`/`,_,_.approvalsReviewer,{threadId:t}),b=await e.sendRequest(`thread/resume`,";

function timestamp() {
  return new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function main() {
  if (!fs.existsSync(targetPath)) {
    throw new Error(`Target file not found: ${targetPath}`);
  }

  const original = fs.readFileSync(targetPath, "utf8");
  if (original.includes(PATCH_TAG)) {
    console.log(`Patch already present in: ${targetPath}`);
    return;
  }

  const patched = original.replace(insertionAnchor, replacement);
  if (patched === original) {
    throw new Error("Patch anchor not found; extension asset layout changed.");
  }

  const backupDir = path.join(
    BACKUP_ROOT,
    `${timestamp()}-codex-resume-local-override`,
  );
  ensureDir(backupDir);
  const backupPath = path.join(backupDir, path.basename(targetPath) + ".bak");
  fs.copyFileSync(targetPath, backupPath);
  fs.writeFileSync(targetPath, patched, "utf8");

  console.log(`Backed up original asset to: ${backupPath}`);
  console.log(`Patched live-resume override into: ${targetPath}`);
  console.log(
    `Override conversationId: ${TARGET_CONVERSATION_ID}`,
  );
}

main();
