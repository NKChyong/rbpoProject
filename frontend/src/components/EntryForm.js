import React, { useState, useEffect } from 'react';
import './EntryForm.css';

function EntryForm({ entry, onSubmit, onCancel }) {
  const [formData, setFormData] = useState({
    title: '',
    kind: 'book',
    link: '',
    status: 'to_read',
    description: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (entry) {
      setFormData({
        title: entry.title || '',
        kind: entry.kind || 'book',
        link: entry.link || '',
        status: entry.status || 'to_read',
        description: entry.description || '',
      });
    }
  }, [entry]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save entry');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="entry-form">
      {error && <div className="error">{error}</div>}

      <div className="form-group">
        <label>Title *</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          placeholder="Enter title"
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Type *</label>
          <select
            name="kind"
            value={formData.kind}
            onChange={handleChange}
            required
          >
            <option value="book">📖 Book</option>
            <option value="article">📄 Article</option>
            <option value="video">🎥 Video</option>
            <option value="podcast">🎙️ Podcast</option>
            <option value="other">📌 Other</option>
          </select>
        </div>

        <div className="form-group">
          <label>Status *</label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            required
          >
            <option value="to_read">To Read</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label>Link (optional)</label>
        <input
          type="url"
          name="link"
          value={formData.link}
          onChange={handleChange}
          placeholder="https://example.com"
        />
      </div>

      <div className="form-group">
        <label>Description (optional)</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Add notes or description"
          rows="4"
        />
      </div>

      <div className="form-actions">
        <button
          type="button"
          onClick={onCancel}
          className="btn btn-outline"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Saving...' : (entry ? 'Update' : 'Create')}
        </button>
      </div>
    </form>
  );
}

export default EntryForm;
