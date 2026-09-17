package com.twm.twmbe.service;

import com.twm.twmbe.entity.BrowseHistory;
import org.springframework.data.domain.Page;

public interface BrowseHistoryService {
    Page<BrowseHistory> getBrowseHistory(Long userId, int page, int size);
    BrowseHistory addBrowseHistory(Long userId, Long postId);
    void removeBrowseHistory(Long historyId);
    void clearUserHistory(Long userId);
    Long getHistoryCountByUserId(Long userId);
}