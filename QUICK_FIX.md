# "This process is not trusted" 경고 해결

## 문제
```
This process is not trusted! Input event monitoring will not be possible 
until it is added to accessibility clients.
```

## 원인
macOS 보안: pynput이 키보드 모니터링 시도 (SHIFT+SPACE 기능)

## 영향
- ✅ 음성 모드: 정상 작동
- ✅ AI 작업: 정상 작동
- ❌ SHIFT+SPACE 단축키: 작동 안함 (선택 기능)

## 해결 방법

### 방법 1: 접근성 권한 부여 (권장)
1. System Settings
2. Privacy & Security
3. Accessibility
4. Terminal 추가
5. 재실행

### 방법 2: 경고 무시
- 시스템은 정상 작동
- SHIFT+SPACE만 안됨
- 그냥 사용해도 OK!

## 결론
**치명적 오류 아님!** 무시하고 사용 가능 ✅
