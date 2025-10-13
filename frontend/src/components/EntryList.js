import React from 'react';
import './EntryList.css';

const kindEmojis = {
  book: '📖',
  article: '📄',
  video: '🎥',
  podcast: '🎙️',
  other: '📌',
};

const statusColors = {
  to_read: '#fbbf24',
  in_progress: '#3b82f6',
  completed: '#10b981',
  archived: '#6b7280',
};

const statusLabels = {
  to_read: 'To Read',
  in_progress: 'In Progress',
  completed: 'Completed',
  archived: 'Archived',
};

function EntryList({ entries, onEdit, onDelete }) {
  if (entries.length === 0) {
    return (
      <div className="empty-state card">
        <h2>📚 No entries yet</h2>
        <p>Start building your reading list by adding your first entry!</p>
      </div>
    );
  }

  return (
    <div className="entry-grid">
      {entries.map((entry) => (
        <div key={entry.id} className="entry-card card">
          <div className="entry-header">
            <span className="entry-kind">{kindEmojis[entry.kind]}</span>
            <span
              className="entry-status"
              style={{ background: statusColors[entry.status] }}
            >
              {statusLabels[entry.status]}
            </span>
          </div>

          <h3 className="entry-title">{entry.title}</h3>

          {entry.description && (
            <p className="entry-description">{entry.description}</p>
          )}

          {entry.link && (
            <a
              href={entry.link}
              target="_blank"
              rel="noopener noreferrer"
              className="entry-link"
            >
              🔗 View Source
            </a>
          )}

          <div className="entry-footer">
            <span className="entry-date">
              {new Date(entry.created_at).toLocaleDateString()}
            </span>
            <div className="entry-actions">
              <button
                onClick={() => onEdit(entry)}
                className="btn-icon"
                title="Edit"
              >
                ✏️
              </button>
              <button
                onClick={() => onDelete(entry.id)}
                className="btn-icon"
                title="Delete"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default EntryList;
