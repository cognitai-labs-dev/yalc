# Testing Guidelines

## General Principles

- **Do not overtest.** Test behavior, not implementation details.
- **Do not overmock.** Mock only expensive external dependencies (databases, APIs, network calls). Everything else should use real objects.
- **Do not over-DRY.** Repeating yourself in tests is fine — prefer explicit, readable tests over clever abstractions.
- **No logic in tests.** Avoid loops, conditionals, and operators. If you feel like you need a "test for the test", the test is too complex.
- **Don't use test classes.** Write plain test functions.
- **Criticize tests in MR reviews.** Tests deserve the same scrutiny as production code.

## Naming

Use descriptive test names that explain the scenario and expected outcome:

```python
# Bad
def test_process():

# Good
def test_process_returns_empty_list_when_no_items_match_filter():
```

## Structure: Arrange / Act / Assert

Separate each test into three distinct sections:

```python
def test_order_total_includes_discount():
    # Arrange
    order = Order(
        items=[Item(price=100), Item(price=200)],
        discount_percent=10,
    )

    # Act
    total = order.calculate_total()

    # Assert
    assert total == 270
```

### Arrange

- Contains **all** information needed to understand the assertion — nothing more.
- **Hardcode plain values.** Don't reuse constants from production code.
- **Limit the number of inputs.** More inputs = less clarity.
- **Comment why each record matters.** When arranging multiple rows that test filtering, add a short comment explaining whether each row should match or why it won't:

```python
# matching status and role
create_user(status="active", role="admin")
# matching status but wrong role
create_user(status="active", role="viewer")
# matching role but wrong status
create_user(status="inactive", role="admin")
```

### Assert

- Only add failure messages when the assertion **isn't self-explanatory** — not on every assert:

```python
# Clear on its own — no message needed
assert total == 270

# Unclear without context — add a message
assert result.status == "active", f"Expected active status but got '{result.status}' for user {user.id}"
```

## Parametrized Tests

Always use IDs to make test output readable:

```python
@pytest.mark.parametrize(
    "input_value, expected",
    [
        pytest.param(0, "zero", id="zero"),
        pytest.param(1, "one", id="positive"),
        pytest.param(-1, "negative", id="negative"),
    ],
)
def test_classify_number(input_value, expected):
    assert classify(input_value) == expected
```

## Fixtures

- **Check existing fixtures** before creating new ones.
- **Don't create multi-purpose fixtures** that try to fit many different scenarios. Keep them focused.
- **Add docstrings** to every fixture — it helps discovery via `pytest --fixtures`:

```python
@pytest.fixture
def expired_subscription():
    """A subscription that expired yesterday with no renewal."""
    return Subscription(
        plan="basic",
        expires_at=date.today() - timedelta(days=1),
        auto_renew=False,
    )
```

## AI-Generated Tests

When using Claude or other AI tools to generate tests, **always refactor** the output so it is obvious to a colleague. AI-generated tests tend to be overly complicated — simplify them to follow these guidelines.
