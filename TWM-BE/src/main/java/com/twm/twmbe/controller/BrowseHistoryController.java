package com.twm.twmbe.controller;

import com.twm.twmbe.entity.BrowseHistory;
import com.twm.twmbe.service.BrowseHistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/history")
@CrossOrigin(origins = "*")
public class BrowseHistoryController {

    @Autowired
    private BrowseHistoryService browseHistoryService;

    @GetMapping("/user/{userId}")
    public ResponseEntity<Map<String, Object>> getBrowseHistory(
            @PathVariable Long userId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {

        Page<BrowseHistory> history = browseHistoryService.getBrowseHistory(userId, page, size);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("data", history.getContent());
        response.put("currentPage", page);
        response.put("totalPages", history.getTotalPages());
        response.put("totalElements", history.getTotalElements());
        response.put("hasNext", history.hasNext());

        return ResponseEntity.ok(response);
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> addBrowseHistory(
            @RequestBody Map<String, Long> request) {
        try {
            Long userId = request.get("userId");
            Long postId = request.get("postId");

            BrowseHistory history = browseHistoryService.addBrowseHistory(userId, postId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("data", history);
            response.put("message", "浏览记录添加成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> removeBrowseHistory(@PathVariable Long id) {
        try {
            browseHistoryService.removeBrowseHistory(id);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "删除浏览记录成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @DeleteMapping("/user/{userId}")
    public ResponseEntity<Map<String, Object>> clearUserHistory(@PathVariable Long userId) {
        try {
            browseHistoryService.clearUserHistory(userId);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "清空浏览记录成功");
            return ResponseEntity.ok(response);
        } catch (RuntimeException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        }
    }

    @GetMapping("/user/{userId}/count")
    public ResponseEntity<Map<String, Object>> getHistoryCount(@PathVariable Long userId) {
        Long count = browseHistoryService.getHistoryCountByUserId(userId);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("count", count);
        return ResponseEntity.ok(response);
    }
}