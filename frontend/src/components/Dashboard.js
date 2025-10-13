import React, { useState, useEffect } from 'react';
import { entriesAPI } from '../services/api';
import EntryList from './EntryList';
import EntryForm from './EntryForm';
import './Dashboard.css';

function Dashboard({ onLogout }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);

  useEffect(() => {
    fetchEntries();
  }, [statusFilter]);

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await entriesAPI.list(params);
      setEntries(response.data.items);
      setError('');
    } catch (err) {
      setError('Failed to load entries');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEntry = async (data) => {
    try {
      await entriesAPI.create(data);
      setShowForm(false);
      fetchEntries();
    } catch (err) {
      throw err;
    }
  };

  const handleUpdateEntry = async (id, data) => {
    try {
      await entriesAPI.update(id, data);
      setEditingEntry(null);
      setShowForm(false);
      fetchEntries();
    } catch (err) {
      throw err;
    }
  };

  const handleDeleteEntry = async (id) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      try {
        await entriesAPI.delete(id);
        fetchEntries();
      } catch (err) {
        setError('Failed to delete entry');
      }
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingEntry(null);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <h1>📚 My Reading List</h1>
            <button onClick={onLogout} className="btn btn-outline">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="container">
          {error && <div className="error">{error}</div>}

          <div className="dashboard-controls">
            <div className="filter-group">
              <label>Filter by status:</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="filter-select"
              >
                <option value="">All</option>
                <option value="to_read">To Read</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="archived">Archived</option>
              </select>
            </div>

            <button
              onClick={() => {
                setEditingEntry(null);
                setShowForm(true);
              }}
              className="btn btn-primary"
            >
              + Add New Entry
            </button>
          </div>

          {showForm && (
            <div className="form-modal">
              <div className="form-modal-content card">
                <h2>{editingEntry ? 'Edit Entry' : 'New Entry'}</h2>
                <EntryForm
                  entry={editingEntry}
                  onSubmit={editingEntry ?
                    (data) => handleUpdateEntry(editingEntry.id, data) :
                    handleCreateEntry
                  }
                  onCancel={handleCancelForm}
                />
              </div>
            </div>
          )}

          {loading ? (
            <div className="loading">Loading entries...</div>
          ) : (
            <EntryList
              entries={entries}
              onEdit={handleEdit}
              onDelete={handleDeleteEntry}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
