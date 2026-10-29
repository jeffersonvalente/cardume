---
name: spring-transfer-service
plugins: ["../..", "../../../cardume-core"]
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Review this Spring Boot 3 service (Java 21). Money transfers occasionally end up with the source debited but the target not credited, and the controller is hard to test.

```java
@RestController
public class TransferController {
  @Autowired AccountRepository repo;

  @PostMapping("/transfer")
  public String transfer(@RequestParam Long from, @RequestParam Long to, @RequestParam double amount) {
    Account a = repo.findById(from).get();
    Account b = repo.findById(to).get();
    a.setBalance(a.getBalance() - amount);
    repo.save(a);
    if (amount > 10000) throw new RuntimeException("limit");
    b.setBalance(b.getBalance() + amount);
    repo.save(b);
    return "ok";
  }
}
```
