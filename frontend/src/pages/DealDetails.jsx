import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api';


const getFileParts = (url) => {
  if (!url) return { name: '', ext: '' };
  const full = decodeURIComponent(url.split('/').pop());
  const lastDot = full.lastIndexOf('.');

  if (lastDot === -1 || lastDot === 0) return { name: full, ext: '' };

  return {
    name: full.substring(0, lastDot),
    ext: full.substring(lastDot)
  };
};

function DealDetails() {
  const { id } = useParams();
  const [deal, setDeal] = useState(null);
  const [company, setCompany] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [comments, setComments] = useState([]);

  const [newComment, setNewComment] = useState('');
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/deals/${id}/`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'new_comment') {
        setComments((prevComments) => {
          const existingIndex = prevComments.findIndex(c => c.id === data.comment.id);

          if (existingIndex !== -1) {
            const newComments = [...prevComments];
            newComments[existingIndex] = data.comment;
            return newComments;
          }
          return [data.comment, ...prevComments];
        });
      }
    };

    return () => socket.close();
  }, [id]);

  useEffect(() => {
    fetchAllDealData();
  }, [id]);

  const fetchAllDealData = async () => {
    try {
      const dealRes = await api.get(`sales/deals/${id}/`);
      const dealData = dealRes.data;
      setDeal(dealData);

      const commentsRes = await api.get(`sales/notes/?deal=${id}`);
      setComments(commentsRes.data);

      if (dealData.company) {
        const companyRes = await api.get(`clients/companies/${dealData.company}/`);
        setCompany(companyRes.data);

        const contactsRes = await api.get(`clients/contacts/?company=${dealData.company}`);
        setContacts(contactsRes.data);
      }

      setLoading(false);
    } catch (err) {
      console.error("Error fetching deal details:", err);
      setError("Failed to load deal details.");
      setLoading(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim() && !file) return;

    const formData = new FormData();
    formData.append('deal', id);
    formData.append('text', newComment);
    if (file) {
      formData.append('attachment', file);
    }

    try {
      const response = await api.post('sales/notes/', formData);

      setComments([response.data, ...comments]);
      setNewComment('');
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      if (textareaRef.current) textareaRef.current.style.height = 'auto';
    } catch (err) {
      alert("Failed to add comment.");
    }
  };

  if (loading) return <div className="flex justify-center mt-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  if (error) return <div className="alert alert-error mt-10">{error}</div>;
  if (!deal) return <div className="text-center mt-10">Deal not found.</div>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center space-x-4 mb-8">
        <Link to="/deals" className="btn btn-sm btn-ghost">← Back to Deals</Link>
        <h1 className="text-3xl font-bold">{deal.title}</h1>
        <div className="badge badge-primary badge-sm md:badge-lg whitespace-nowrap">${deal.value} {deal.currency}</div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <div className="lg:col-span-1 space-y-6">

          {/* Deals block */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-lg border-b pb-2">Deal Information</h2>
              <div className="space-y-2 mt-2">
                <p><span className="font-semibold text-base-content/70">Expected Close:</span> {deal.close_date ? deal.close_date.split('T')[0] : 'N/A'}</p>
                <p><span className="font-semibold text-base-content/70">Manager:</span> {deal.owner_name || 'N/A'}</p>
                <p><span className="font-semibold text-base-content/70">Created:</span> {new Date(deal.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Company block */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-lg border-b pb-2">Company Information</h2>
              {company ? (
                <div className="space-y-2 mt-2">
                  <p className="font-bold text-xl">{company.name}</p>
                  <p><span className="font-semibold text-base-content/70">Industry:</span> {company.industry || 'N/A'}</p>
                  <p><span className="font-semibold text-base-content/70">Website:</span> {company.website ? <a href={company.website} target="_blank" rel="noreferrer" className="link link-primary">{company.website}</a> : 'N/A'}</p>
                  <p><span className="font-semibold text-base-content/70">Address:</span> {company.address || 'N/A'}</p>
                </div>
              ) : (
                <p className="text-base-content/50 italic mt-2">No company linked to this deal.</p>
              )}
            </div>
          </div>

          {/* Contacts block */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title text-lg border-b pb-2">Associated Contacts</h2>
              {contacts.length > 0 ? (
                <ul className="space-y-3 mt-2">
                  {contacts.map(contact => (
                    <li key={contact.id} className="bg-base-200 p-3 rounded-lg">
                      <p className="font-bold">{contact.first_name} {contact.last_name}</p>
                      <p className="text-sm">{contact.email}</p>
                      <p className="text-sm text-primary">{contact.phone}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-base-content/50 italic mt-2">No contacts found for this company.</p>
              )}
            </div>
          </div>

        </div>
        {/* Comments (Notes) block */}
        <div className="lg:col-span-2">
          <div className="card bg-base-100 shadow-xl h-[calc(100vh-12rem)] min-h-[600px] flex flex-col">
            <div className="card-body flex flex-col overflow-hidden p-4 lg:p-6">
              <h2 className="card-title text-xl border-b pb-2 mb-4 shrink-0">Manager Comments & History</h2>

              {/* Comments list */}
              <div className="flex-1 overflow-y-auto space-y-4 pr-2 mb-4">
                {comments.length === 0 ? (
                  <div className="text-center text-base-content/50 mt-10">No comments yet.</div>
                ) : (
                  comments.map(comment => (
                    <div key={comment.id} className="chat chat-start">
                      <div className="chat-header mb-1">
                        <span className="font-bold">{comment.created_by_name || 'User'}</span>
                        <time className="text-xs opacity-50 ml-2">
                          {new Date(comment.created_at).toLocaleString()}
                        </time>
                      </div>
                      <div className="chat-bubble bg-base-100 text-base-content shadow-md border border-base-200">

                        <div className="whitespace-pre-wrap break-words">
                          {comment.text}
                        </div>

                        {comment.attachment && (
                          <div className="mt-3 pt-3 border-t border-base-300">
                            {(() => {
                              const { name, ext } = getFileParts(comment.attachment);
                              return (
                                <a
                                  href={comment.attachment}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  title={name + ext}
                                  className="btn btn-sm btn-outline btn-primary w-[200px] justify-start flex-nowrap overflow-hidden"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                                  </svg>

                                  <div className="flex flex-nowrap overflow-hidden text-left">
                                    <span className="truncate">{name}</span>
                                    <span className="shrink-0">{ext}</span>
                                  </div>
                                </a>
                              );
                            })()}
                          </div>
                        )}

                        {comment.original_text && (
                          <details className="mt-3 pt-3 border-t border-base-300 group cursor-pointer">
                            <summary className="text-xs opacity-60 font-medium hover:opacity-100 transition-opacity list-none flex items-center">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                              </svg>
                              View original text
                            </summary>
                            <div className="mt-2 text-sm opacity-70 whitespace-pre-wrap pl-4 border-l-2 border-base-300 italic">
                              {comment.original_text}
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Input form */}
              <form onSubmit={handleAddComment} className="flex flex-col space-y-2 shrink-0 pt-4 border-t border-base-200">
                <textarea
                  ref={textareaRef}
                  placeholder="Write an update... (Shift+Enter for new line)"
                  className="textarea textarea-bordered w-full min-h-[50px] max-h-[200px] leading-relaxed resize-none overflow-y-auto"
                  value={newComment}
                  onChange={(e) => {
                    setNewComment(e.target.value);
                    e.target.style.height = 'auto';
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleAddComment(e);
                    }
                  }}
                />

                <div className="flex justify-between items-center">
                  {/* File upload button */}
                  <input
                    type="file"
                    className="file-input file-input-bordered file-input-sm w-full max-w-xs"
                    onChange={(e) => setFile(e.target.files[0])}
                    ref={fileInputRef}
                  />
                  <button type="submit" className="btn btn-primary btn-sm">Add Note</button>
                </div>
              </form>

            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

export default DealDetails;