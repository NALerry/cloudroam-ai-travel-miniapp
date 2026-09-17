// UserCollectionService.java
package com.twm.twmbe.service;

import com.twm.twmbe.entity.UserCollection;
import org.springframework.data.domain.Page;

public interface UserCollectionService {
    Page<UserCollection> getUserCollections(Long userId, int page, int size);
    UserCollection addCollection(Long userId, Long postId);
    void removeCollection(Long userId, Long postId);
    void removeCollectionById(Long collectionId);
    boolean isCollected(Long userId, Long postId);
    Long getCollectionCountByUserId(Long userId);
}