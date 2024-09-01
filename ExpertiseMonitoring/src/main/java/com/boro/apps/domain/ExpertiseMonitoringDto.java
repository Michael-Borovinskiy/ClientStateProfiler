package com.boro.apps.domain;


import java.sql.Timestamp;

public record ExpertiseMonitoringDto(Long id, String expertiseType, String clientId, String status, String comment, Timestamp dtExpertiseStatus) {
}
