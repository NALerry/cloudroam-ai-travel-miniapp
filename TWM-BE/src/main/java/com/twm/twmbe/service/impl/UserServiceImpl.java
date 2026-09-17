// UserServiceImpl.java
package com.twm.twmbe.service.impl;

import com.twm.twmbe.entity.User;
import com.twm.twmbe.repository.UserRepository;
import com.twm.twmbe.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在，ID: " + id));
    }

    @Override
    public User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在，用户名: " + username));
    }

    @Override
    @Transactional
    public User updateUser(Long id, User user) {
        User existing = getUserById(id);

        // 更新允许修改的字段
        if (user.getNickname() != null) {
            existing.setNickname(user.getNickname());
        }
        if (user.getBio() != null) {
            existing.setBio(user.getBio());
        }
        if (user.getGender() != null) {
            existing.setGender(user.getGender());
        }
        if (user.getBirthday() != null) {
            existing.setBirthday(user.getBirthday());
        }
        if (user.getPhone() != null) {
            existing.setPhone(user.getPhone());
        }
        if (user.getEmail() != null) {
            existing.setEmail(user.getEmail());
        }
        if (user.getLocation() != null) {
            existing.setLocation(user.getLocation());
        }
        if (user.getPreferredTravelTypes() != null) {
            existing.setPreferredTravelTypes(user.getPreferredTravelTypes());
        }
        if (user.getFrequentDestinations() != null) {
            existing.setFrequentDestinations(user.getFrequentDestinations());
        }
        if (user.getSocialLinks() != null) {
            existing.setSocialLinks(user.getSocialLinks());
        }

        return userRepository.save(existing);
    }

    @Override
    @Transactional
    public User updateUserAvatar(Long id, String avatarUrl) {
        User user = getUserById(id);
        user.setAvatar(avatarUrl);
        return userRepository.save(user);
    }

    @Override
    @Transactional
    public void updateUserStats(Long userId) {
        // 更新用户统计信息（帖子数、粉丝数等）
        User user = getUserById(userId);
        // 这里可以添加统计逻辑
        userRepository.save(user);
    }

    @Override
    public boolean checkUsernameExists(String username) {
        return userRepository.existsByUsername(username);
    }

    @Override
    public boolean checkPhoneExists(String phone) {
        return userRepository.existsByPhone(phone);
    }

    @Override
    public boolean checkEmailExists(String email) {
        return userRepository.existsByEmail(email);
    }
}