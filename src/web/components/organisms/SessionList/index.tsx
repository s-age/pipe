import React, { JSX } from "react";

import Button from "@/components/atoms/Button";
import Heading from "@/components/atoms/Heading";
import { h2Style } from "@/components/atoms/Heading/style.css";

import {
  sessionListColumn,
  sessionListContainer,
  sessionListItem,
  sessionLink,
  sessionLinkActive,
  sessionIdStyle,
  stickyNewChatButtonContainer,
} from "./style.css";

type SessionListProps = {
  sessions: [string, { purpose: string; [key: string]: any }][];
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
};

const SessionList = ({
  sessions,
  currentSessionId,
  onSessionSelect,
}: SessionListProps): JSX.Element => {
  // セッションツリーを構築するヘルパー関数
  const buildSessionTree = (sessionsData: [string, { purpose: string }][]) => {
    const tree: any = {};
    sessionsData.forEach(([id, meta]) => {
      const parts = id.split("/");
      let currentLevel = tree;
      parts.forEach((part, index) => {
        if (!currentLevel[part]) {
          currentLevel[part] = { meta: null, children: {} };
        }
        if (index === parts.length - 1) {
          currentLevel[part].meta = meta;
          currentLevel[part].id = id;
        }
        currentLevel = currentLevel[part].children;
      });
    });

    return tree;
  };

  const createNode = (branch: any, level: number) => {
    const items: React.ReactNode[] = [];
    for (const key in branch) {
      const node = branch[key];
      if (node.meta) {
        items.push(
          <li key={node.id} className={sessionListItem}>
            <a
              href={`/session/${node.id}`}
              className={`${sessionLink} ${node.id === currentSessionId ? sessionLinkActive : ""}`.trim()}
              onClick={(e) => {
                e.preventDefault();
                onSessionSelect(node.id);
              }}
            >
              {node.meta.purpose}{" "}
              <p className={sessionIdStyle}>{node.id.substring(0, 8)}</p>
            </a>
            {Object.keys(node.children).length > 0 && (
              <ul style={{ paddingLeft: "20px" }}>
                {createNode(node.children, level + 1)}
              </ul>
            )}
          </li>,
        );
      } else if (Object.keys(node.children).length > 0) {
        // メタデータがないが子がある場合（中間ディレクトリ）
        items.push(
          <li key={key} className={sessionListItem}>
            <span style={{ fontWeight: "bold" }}>{key}</span>
            <ul style={{ paddingLeft: "20px" }}>
              {createNode(node.children, level + 1)}
            </ul>
          </li>,
        );
      }
    }

    return items;
  };

  const sessionTree = buildSessionTree(sessions);

  return (
    <div className={sessionListColumn}>
      <Heading level={2} className={h2Style}>
        Sessions
      </Heading>
      <ul className={sessionListContainer}>{createNode(sessionTree, 0)}</ul>
      <div className={stickyNewChatButtonContainer}>
        <Button
          kind="primary"
          size="default"
          onClick={() => (window.location.href = "/new_session")}
        >
          + New Chat
        </Button>
      </div>
    </div>
  );
};

export default SessionList;
