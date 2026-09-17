// UserCollectionController.java
package com.twm.twmbe.controller;

import com.twm.twmbe.entity.UserCollection;
import com.twm.twmbe.service.UserCollectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/collections")
@CrossOrigin(origins = "*")
public class UserCollectionController {

    @Autowired
    private UserCollectionService userCollectionService;

    @GetMapping("/user/{userId}")
    public ResponseEntity<Map<String, Object>> getUserCollections(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<UserCollection> collections = userCollectionService.getUserCollections(userId, page, size);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", collections.getContent());
        response.put("currentPage", page);
        response.put("totalPages", collections.getTotalPages());
        response.put("totalElements", collections.getTotalElements());
        response.put("hasNext", collections.hasNext());

        return ResponseEntity.ok(response);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addCollection(
            @RequestBody Map<String, Long> request) {
        try {
            Long userId = request.get("userId");
            Long postId = request.get("postId");

            UserCollection collection = userCollectionService.addCollection(userId, postId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", collection);
            response.put("message", "收藏成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> removeCollection(@PathVariable Long id) {
        try {
            userCollectionService.removeCollectionById(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "取消收藏成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/user/{userId}/post/{postId}")
    public ResponseEntity<Map<String, Object>> removeCollectionByUserAndPost(
            @PathVariable Long userId,
            @PathVariable Long postId) {
        try {
            userCollectionService.removeCollection(userId, postId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "取消收藏成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/user/{userId}/check/{postId}")
    public ResponseEntity<Map<String, Object>> checkCollected(
            @PathVariable Long userId,
            @PathVariable Long postId) {
        boolean isCollected = userCollectionService.isCollected(userId, postId);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("collected", isCollected);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/user/{userId}/count")
    public ResponseEntity<Map<String, Object>> getCollectionCountByUser(@PathVariable Long userId) {
        Long count = userCollectionService.getCollectionCountByUserId(userId);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("count", count);
        return ResponseEntity.ok(response);
    }
}