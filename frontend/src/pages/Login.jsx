import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/api/accounts/login/', {
                username,
                password
            });
            
            localStorage.setItem('access', response.data.access);
            localStorage.setItem('refresh', response.data.refresh);
            
            navigate('/');
        } catch (err) {
            setError('Invalid credentials. Please try again.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-base-200">
            <div className="card w-96 bg-base-100 shadow-xl">
                <div className="card-body">
                    <h2 className="card-title justify-center text-2xl font-bold mb-4">CRM Login</h2>
                    {error && <div className="alert alert-error text-sm p-2 rounded">{error}</div>}
                    
                    <form onSubmit={handleLogin}>
                        <div className="form-control w-full max-w-xs mb-4">
                            <label className="label"><span className="label-text">Username</span></label>
                            <input 
                                type="text" 
                                placeholder="Enter your username" 
                                className="input input-bordered w-full max-w-xs" 
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required 
                            />
                        </div>
                        
                        <div className="form-control w-full max-w-xs mb-6">
                            <label className="label"><span className="label-text">Password</span></label>
                            <input 
                                type="password" 
                                placeholder="Enter your password" 
                                className="input input-bordered w-full max-w-xs" 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required 
                            />
                        </div>
                        
                        <button type="submit" className="btn btn-primary w-full">Sign In</button>
                    </form>
                    
                    <p className="text-center text-sm">
                        Need an account? <Link to="/register" className="link link-primary">You can create it here</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Login;