// UserController.java
package com.twm.twmbe.controller;

import com.twm.twmbe.entity.User;
import com.twm.twmbe.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {

    @Autowired
    private UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getUserById(@PathVariable Long id) {
        try {
            User user = userService.getUserById(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", user);
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/username/{username}")
    public ResponseEntity<Map<String, Object>> getUserByUsername(@PathVariable String username) {
        try {
            User user = userService.getUserByUsername(username);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", user);
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateUser(@PathVariable Long id, @RequestBody User user) {
        try {
            User updatedUser = userService.updateUser(id, user);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", updatedUser);
            response.put("message", "用户信息更新成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @PutMapping("/{id}/avatar")
    public ResponseEntity<Map<String, Object>> updateUserAvatar(@PathVariable Long id, @RequestBody Map<String, String> request) {
        try {
            String avatarUrl = request.get("avatar");
            User updatedUser = userService.updateUserAvatar(id, avatarUrl);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", updatedUser);
            response.put("message", "头像更新成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/check/username/{username}")
    public ResponseEntity<Map<String, Object>> checkUsernameExists(@PathVariable String username) {
        boolean exists = userService.checkUsernameExists(username);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("exists", exists);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/check/phone/{phone}")
    public ResponseEntity<Map<String, Object>> checkPhoneExists(@PathVariable String phone) {
        boolean exists = userService.checkPhoneExists(phone);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("exists", exists);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/check/email/{email}")
    public ResponseEntity<Map<String, Object>> checkEmailExists(@PathVariable String email) {
        boolean exists = userService.checkEmailExists(email);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("exists", exists);
        return ResponseEntity.ok(response);
    }
}