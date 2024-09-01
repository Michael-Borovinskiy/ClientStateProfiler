package com.boro.apps.domain;

import jakarta.persistence.*;
import lombok.*;

import java.sql.Timestamp;

@AllArgsConstructor
@NoArgsConstructor
@Builder
@Getter
@Setter
@Entity
@Table(name = "EXPERTISES")
public class ExpertiseMonitoring {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "expertise_type", length = 30)
    @Enumerated(EnumType.STRING)
    private ExpertiseType expertiseType;

    @Column(name = "client_id", length = 36 )
    private String clientId;

    @Column(name = "status", length = 30)
    private String status;

    @Column(name = "comment", length = 1000)
    private String comment;

    @Column(name = "dt_expertise_status")
    private Timestamp dtExpertiseStatus;

    public ExpertiseMonitoring(ExpertiseType expertiseType, String clientId, String status, String comment, Timestamp dtExpertiseStatus) {
        this.expertiseType = expertiseType;
        this.clientId = clientId;
        this.status = status;
        this.comment = comment;
        this.dtExpertiseStatus = dtExpertiseStatus;
    }

    public ExpertiseMonitoringDto toDto() {
        return new ExpertiseMonitoringDto(
                this.getId(),
                this.getExpertiseType().name(),
                this.getClientId(),
                this.getStatus(),
                this.getComment(),
                this.getDtExpertiseStatus());
    }
}

