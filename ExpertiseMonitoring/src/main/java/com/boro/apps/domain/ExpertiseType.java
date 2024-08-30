package com.boro.apps.domain;

public enum ExpertiseType {
    TURNOVER_INCREASE("1Dff03"),
    ACCOUNT_LOCK("3Dzx05"),
    SUPPLIER_LOSS("6Dix30");

    private String code;

    ExpertiseType(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }


}