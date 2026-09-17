// UserRepository.java
package com.twm.twmbe.repository;

import com.twm.twmbe.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByUsername(String username);

    Optional<User> findByPhone(String phone);

    Optional<User> findByEmail(String email);

    boolean existsByUsername(String username);

    boolean existsByPhone(String phone);

    boolean existsByEmail(String email);

    @Modifying
    @Query("UPDATE User u SET u.followCount = u.followCount + 1 WHERE u.id = :userId")
    void incrementFollowCount(@Param("userId") Long userId);

    @Modifying
    @Query("UPDATE User u SET u.followCount = u.followCount - 1 WHERE u.id = :userId AND u.followCount > 0")
    void decrementFollowCount(@Param("userId") Long userId);

    @Modifying
    @Query("UPDATE User u SET u.fansCount = u.fansCount + 1 WHERE u.id = :userId")
    void incrementFansCount(@Param("userId") Long userId);

    @Modifying
    @Query("UPDATE User u SET u.fansCount = u.fansCount - 1 WHERE u.id = :userId AND u.fansCount > 0")
    void decrementFansCount(@Param("userId") Long userId);

    @Modifying
    @Query("UPDATE User u SET u.postCount = u.postCount + 1 WHERE u.id = :userId")
    void incrementPostCount(@Param("userId") Long userId);

    @Modifying
    @Query("UPDATE User u SET u.postCount = u.postCount - 1 WHERE u.id = :userId AND u.postCount > 0")
    void decrementPostCount(@Param("userId") Long userId);
}