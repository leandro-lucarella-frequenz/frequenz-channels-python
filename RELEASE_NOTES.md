# Frequenz channels Release Notes

## New Features

- `Receiver`

   * Add `take_while()` as a less ambiguous and more readable alternative to `filter()`.
   * Add `drop_while()` as a convenience and more readable alternative to `filter()` with a negated predicate.
   * The usage of `filter()` is discouraged in favor of `take_while()` and `drop_while()`.

### Experimental

- A new predicate, `OnlyIfPrevious`, to `filter()` messages based on the previous message.
- A new special case of `OnlyIfPrevious`, `ChangedOnly`, to skip messages if they are equal to the previous message.
