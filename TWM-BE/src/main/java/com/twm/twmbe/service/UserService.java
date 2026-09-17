// UserService.java
package com.twm.twmbe.service;

import com.twm.twmbe.entity.User;

public interface UserService {
    User getUserById(Long id);
    User getUserByUsername(String username);
    User updateUser(Long id, User user);
    User updateUserAvatar(Long id, String avatarUrl);
    void updateUserStats(Long userId);
    boolean checkUsernameExists(String username);
    boolean checkPhoneExists(String phone);
    boolean checkEmailExists(String email);
}