import pygame
import numpy as np
import os
import wave
import struct

# Initialize pygame mixer
pygame.mixer.init(44100, -16, 2, 512)

# Create sounds directory if it doesn't exist
os.makedirs('assets/sounds', exist_ok=True)

def save_wave_file(filename, data, framerate=44100):
    """Save wave data to a file"""
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(framerate)
        wav_file.writeframes(data.tobytes())

def create_sound(freq, duration, volume=0.5, decay=True):
    """Create a sound with given frequency, duration, and optional decay"""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave_data = np.sin(2 * np.pi * freq * t)
    
    if decay:
        # Apply exponential decay
        decay_factor = np.exp(-4 * t / duration)
        wave_data *= decay_factor
    
    # Apply volume
    wave_data *= volume * 32767
    
    # Convert to 16-bit integer format
    wave_data = wave_data.astype(np.int16)
    
    # Make stereo by duplicating the wave
    stereo = np.array([wave_data, wave_data]).T.copy()
    return stereo

# Create arrow shoot sound (high-pitched short beep)
shoot_data = create_sound(880, 0.1, volume=0.3)
save_wave_file(os.path.join('assets/sounds', 'shoot.wav'), shoot_data)

# Create explosion sound (low frequency with decay)
explosion_data = create_sound(150, 0.3, volume=0.4, decay=True)
save_wave_file(os.path.join('assets/sounds', 'explosion.wav'), explosion_data)

# Create rescue sound (ascending tones)
rescue_freq = 440
rescue_duration = 0.2
t = np.linspace(0, rescue_duration, int(44100 * rescue_duration))
rescue_wave = np.sin(2 * np.pi * rescue_freq * t * (1 + t/rescue_duration))
rescue_wave = (rescue_wave * 32767 * 0.3).astype(np.int16)
rescue_stereo = np.array([rescue_wave, rescue_wave]).T.copy()
save_wave_file(os.path.join('assets/sounds', 'rescue.wav'), rescue_stereo)

# Create death sound (descending tone with decay)
death_freq = 440
death_duration = 0.5
t = np.linspace(0, death_duration, int(44100 * death_duration))
death_wave = np.sin(2 * np.pi * death_freq * t * (1 - 0.5 * t/death_duration))
decay = np.exp(-5 * t / death_duration)
death_wave *= decay
death_wave = (death_wave * 32767 * 0.4).astype(np.int16)
death_stereo = np.array([death_wave, death_wave]).T.copy()
save_wave_file(os.path.join('assets/sounds', 'death.wav'), death_stereo)

# Create wave clear sound (triumphant jingle)
wave_duration = 0.6
t = np.linspace(0, wave_duration, int(44100 * wave_duration))
wave_clear_wave = (
    np.sin(2 * np.pi * 440 * t) * 0.3 +  # Base note
    np.sin(2 * np.pi * 554 * t) * 0.2 +  # Major third
    np.sin(2 * np.pi * 659 * t) * 0.2    # Perfect fifth
)
wave_clear_wave *= np.exp(-2 * t / wave_duration)  # Add decay
wave_clear_wave = (wave_clear_wave * 32767 * 0.4).astype(np.int16)
wave_clear_stereo = np.array([wave_clear_wave, wave_clear_wave]).T.copy()
save_wave_file(os.path.join('assets/sounds', 'wave_clear.wav'), wave_clear_stereo)

print("Sound effects created successfully in assets/sounds/") 