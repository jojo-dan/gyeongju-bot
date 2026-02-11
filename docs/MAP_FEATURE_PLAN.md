# 지도 기능 기획서 + API 설정 가이드

## 핵심 요약

| 항목 | 카카오맵 | 네이버 지도 |
|------|---------|------------|
| **지도 렌더링** | 사용 (JS SDK) | **신규 가입 불가** (2025.05 차단) |
| **장소 검색/좌표 조회** | 사용 (로컬 API) | 사용 (검색 API, developers.naver.com) |
| **무료 티어** | 지도 일 30만건, 로컬 일 10만건 | 검색 일 25,000건 |
| **비용** | 0원 | 0원 |

> **네이버 지도 API는 2025년 5월부터 신규 이용 신청이 차단되어 지도 렌더링에 사용 불가.**
> 대신 네이버 검색 API(장소 검색)는 별도 서비스로 여전히 무료 사용 가능.

### 최종 전략
- **지도 렌더링**: 카카오맵 JavaScript SDK
- **장소 데이터 교차 검증**: 카카오 로컬 API + 네이버 검색 API
  - 두 API에서 같은 장소를 검색해서 좌표/영업시간/주소를 교차 확인
  - 불일치 시 수동 확인 후 채택

---

## jojo가 해야 할 계정 인증 절차

### A. 카카오 개발자 (지도 + 장소 검색)

#### 1단계: 카카오 개발자 가입
1. https://developers.kakao.com 접속
2. **카카오 계정으로 로그인** (기존 카카오톡 계정 사용 가능)
3. 개발자 약관 동의

#### 2단계: 앱 생성
1. 상단 메뉴 **[내 애플리케이션]** 클릭
2. **[애플리케이션 추가하기]** 클릭
3. 입력:
   - **앱 이름**: `gyeongju-trip` (아무거나 OK)
   - **사업자명**: 본인 이름 입력
4. **저장** 클릭

#### 3단계: 앱 키 확인 & 복사
1. 생성된 앱 클릭 → **[앱 설정] > [앱 키]**
2. 2개 키 복사해두기:
   - **JavaScript 키** → 웹앱 지도 렌더링에 사용 (프론트 노출 OK, 도메인 제한으로 보호)
   - **REST API 키** → 장소 검색에 사용 (서버에서만 사용, 노출 금지)

#### 4단계: 플랫폼(도메인) 등록
1. **[앱 설정] > [플랫폼]** 이동
2. **Web 플랫폼 추가** 클릭
3. 사이트 도메인 입력:
   ```
   https://gyeongju-trip.vercel.app
   ```
4. 개발용도 추가 (선택):
   ```
   http://localhost:3000
   ```

#### 5단계: 카카오맵 API 활성화 (2024.12부터 필수!)
1. **[제품 설정] > [카카오맵]** 이동
2. **활성화 설정 → ON** 전환
3. 이걸 안 하면 지도가 안 뜸!

#### 완료 후 나한테 알려줄 것
```
카카오 JavaScript 키: _______________
카카오 REST API 키: _______________
```

---

### B. 네이버 개발자 (장소 검색 교차 검증용)

> 네이버 **지도 API**는 신규 가입 불가이므로, **검색 API**만 사용합니다.
> 검색 API는 https://developers.naver.com 에서 별도로 발급받습니다.

#### 1단계: 네이버 개발자 가입
1. https://developers.naver.com 접속
2. **네이버 계정으로 로그인**
3. 개발자 약관 동의

#### 2단계: 애플리케이션 등록
1. 상단 메뉴 **[Application] > [내 애플리케이션]**
2. **[Application 등록]** 클릭
3. 입력:
   - **애플리케이션 이름**: `gyeongju-trip`
   - **사용 API 선택**: **검색** 체크
   - **비로그인 오픈 API 서비스 환경**: `WEB 설정` 선택
   - **웹 서비스 URL**: `https://gyeongju-trip.vercel.app`
4. **등록하기** 클릭

#### 3단계: 키 확인 & 복사
1. 등록된 애플리케이션 클릭
2. 2개 키 복사:
   - **Client ID**
   - **Client Secret**

#### 완료 후 나한테 알려줄 것
```
네이버 Client ID: _______________
네이버 Client Secret: _______________
```

---

## 전체 체크리스트

- [ ] 카카오 개발자 가입 + 로그인
- [ ] 카카오 앱 생성
- [ ] 카카오 JavaScript 키 / REST API 키 복사
- [ ] 카카오 플랫폼에 `gyeongju-trip.vercel.app` 도메인 등록
- [ ] 카카오맵 API 활성화 ON
- [ ] 네이버 개발자 가입 + 로그인
- [ ] 네이버 애플리케이션 등록 (검색 API)
- [ ] 네이버 Client ID / Client Secret 복사

소요시간: 약 10~15분

---

## 참고 링크

### 카카오
- [Kakao Developers](https://developers.kakao.com/)
- [카카오 API 시작하기](https://developers.kakao.com/docs/latest/ko/tutorial/start)
- [카카오맵 Web API 가이드](https://apis.map.kakao.com/web/guide/)
- [로컬 API 개발 가이드](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [쿼터 정보](https://developers.kakao.com/docs/latest/ko/getting-started/quota)
- [카카오맵 API 활성화 공지](https://devtalk.kakao.com/t/api/141107)

### 네이버
- [NAVER Developers](https://developers.naver.com/)
- [네이버 검색 API 문서](https://developers.naver.com/docs/serviceapi/search/local/local.md)
- [네이버 지도 API 신규 차단 공지](https://www.gov-ncloud.com/v2/support/notice/all/499)
- [네이버 지도 무료 종료 공지](https://www.fin-ncloud.com/support/notice/all/1644)

---

## 구현 계획 (jojo 인증 완료 후)

### Phase 1: 데이터 준비
- JSON에 coords 필드 추가 (카카오+네이버 교차 검증)
- 숙소(까사멜로우) 좌표 고정 추가
- 약 30개 장소 좌표 조회

### Phase 2: 지도 UI 구현
- 카카오맵 SDK 로드
- 하단 바에 "지도" 토글 버튼 추가
- 일별 마커 표시 + 동선 라인
- 커스텀 마커 (카테고리별 아이콘, 상태별 색상)
- 마커 클릭 시 장소 정보 팝업

### Phase 3: 연동 + 폴리싱
- 리스트-지도 상호 연동
- 디자인 감성 통합 (디바이스 스크린 안 지도)
- 모바일 터치 최적화
