import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

function Register() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await axios.post('http://localhost:8000/api/accounts/register/', {
                username,
                email,
                password
            });
            
            setSuccess(true);
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed. Check your information.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-base-200">
            <div className="card w-96 bg-base-100 shadow-xl">
                <div className="card-body">
                    <h2 className="card-title justify-center text-2xl font-bold mb-4">Create Account</h2>
                    
                    {error && <div className="alert alert-error text-sm p-2 rounded">{error}</div>}
                    {success && <div className="alert alert-success text-sm p-2 rounded">Account created! Redirecting to login...</div>}
                    
                    <form onSubmit={handleRegister}>
                        <div className="form-control w-full mb-2">
                            <label className="label"><span className="label-text">Username</span></label>
                            <input 
                                type="text" 
                                className="input input-bordered w-full" 
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required 
                            />
                        </div>

                        <div className="form-control w-full mb-2">
                            <label className="label"><span className="label-text">Email</span></label>
                            <input 
                                type="email" 
                                className="input input-bordered w-full" 
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required 
                            />
                        </div>
                        
                        <div className="form-control w-full mb-6">
                            <label className="label"><span className="label-text">Password</span></label>
                            <input 
                                type="password" 
                                className="input input-bordered w-full" 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required 
                            />
                        </div>
                        
                        <button type="submit" className="btn btn-primary w-full mb-4">Register</button>
                    </form>

                    <p className="text-center text-sm">
                        Already have an account? <Link to="/login" className="link link-primary">Log in here</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Register;