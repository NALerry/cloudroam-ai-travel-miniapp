package com.twm.twmbe.controller;

import com.twm.twmbe.entity.UserLike;
import com.twm.twmbe.service.UserLikeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/likes")
@CrossOrigin(origins = "*")
public class UserLikeController {

    @Autowired
    private UserLikeService userLikeService;

    @GetMapping("/user/{userId}")
    public ResponseEntity<Map<String, Object>> getUserLikes(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<UserLike> likes = userLikeService.getUserLikes(userId, page, size);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", likes.getContent());
        response.put("currentPage", page);
        response.put("totalPages", likes.getTotalPages());
        response.put("totalElements", likes.getTotalElements());
        response.put("hasNext", likes.hasNext());

        return ResponseEntity.ok(response);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addLike(
            @RequestBody Map<String, Long> request) {
        try {
            Long userId = request.get("userId");
            Long postId = request.get("postId");

            UserLike like = userLikeService.addLike(userId, postId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", like);
            response.put("message", "点赞成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> removeLike(@PathVariable Long id) {
        try {
            userLikeService.removeLikeById(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "取消点赞成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/user/{userId}/post/{postId}")
    public ResponseEntity<Map<String, Object>> removeLikeByUserAndPost(
            @PathVariable Long userId,
            @PathVariable Long postId) {
        try {
            userLikeService.removeLike(userId, postId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "取消点赞成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/user/{userId}/check/{postId}")
    public ResponseEntity<Map<String, Object>> checkLiked(
            @PathVariable Long userId,
            @PathVariable Long postId) {
        boolean isLiked = userLikeService.isLiked(userId, postId);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("liked", isLiked);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/user/{userId}/count")
    public ResponseEntity<Map<String, Object>> getLikeCountByUser(@PathVariable Long userId) {
        Long count = userLikeService.getLikeCountByUserId(userId);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("count", count);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/post/{postId}/count")
    public ResponseEntity<Map<String, Object>> getLikeCountByPost(@PathVariable Long postId) {
        Long count = userLikeService.getLikeCountByPostId(postId);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("count", count);
        return ResponseEntity.ok(response);
    }
}