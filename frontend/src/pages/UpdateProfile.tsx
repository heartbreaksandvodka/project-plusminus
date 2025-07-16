import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './UpdateProfile.css';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  profile_picture?: string;
  bio?: string;
  date_of_birth?: string;
  phone_number?: string;
}

const UpdateProfile: React.FC = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
        if (data.profile_picture) {
          setPreviewImage(`http://localhost:8000${data.profile_picture}`);
        }
      }
    } catch (err) {
      setError('Failed to fetch profile');
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setProfileImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      
      if (profile) {
        formData.append('username', profile.username);
        formData.append('first_name', profile.first_name);
        formData.append('last_name', profile.last_name);
        formData.append('bio', profile.bio || '');
        formData.append('date_of_birth', profile.date_of_birth || '');
        formData.append('phone_number', profile.phone_number || '');
        
        if (profileImage) {
          formData.append('profile_picture', profileImage);
        }
      }

      const response = await fetch('http://localhost:8000/api/update-profile/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        setSuccess('Profile updated successfully!');
        fetchProfile(); // Refresh profile data
      } else {
        const data = await response.json();
        setError(data.message || 'Failed to update profile');
      }
    } catch (err) {
      setError('An error occurred while updating profile');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfile(prev => prev ? { ...prev, [name]: value } : null);
  };

  if (!profile) {
    return (
      <div className="update-profile-container">
        <div className="loading">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="update-profile-container">
      <div className="update-profile-content">
        <h2>Update Profile</h2>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <form onSubmit={handleSubmit} className="update-profile-form">
          <div className="profile-image-section">
            <div className="profile-image-preview">
              {previewImage ? (
                <img src={previewImage} alt="Profile preview" />
              ) : (
                <div className="no-image">No Image</div>
              )}
            </div>
            <div className="image-upload">
              <input
                type="file"
                id="profileImage"
                accept="image/*"
                onChange={handleImageChange}
                className="file-input"
              />
              <label htmlFor="profileImage" className="file-label">
                Choose Profile Picture
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={profile.first_name}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Last Name</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={profile.last_name}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={profile.username}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={profile.email}
                disabled
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone_number">Phone Number</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={profile.phone_number || ''}
                onChange={handleInputChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="date_of_birth">Date of Birth</label>
              <input
                type="date"
                id="date_of_birth"
                name="date_of_birth"
                value={profile.date_of_birth || ''}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="bio">Bio</label>
            <textarea
              id="bio"
              name="bio"
              value={profile.bio || ''}
              onChange={handleInputChange}
              rows={4}
              placeholder="Tell us about yourself..."
            />
          </div>

          <div className="form-actions">
            <button type="submit" disabled={loading} className="update-button">
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
            <button 
              type="button" 
              onClick={() => navigate('/dashboard')} 
              className="cancel-button"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UpdateProfile;
