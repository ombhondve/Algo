import { isValidEmail, validateContact } from './validation';

describe('isValidEmail', () => {
  test.each(['a@b.com', 'first.last@mail.co.in'])('accepts %s', (e) => {
    expect(isValidEmail(e)).toBe(true);
  });
  test.each(['', 'abc', 'a@b', 'a@@b.com', 'a b@c.com', null, undefined])('rejects %s', (e) => {
    expect(isValidEmail(e)).toBe(false);
  });
});

describe('validateContact', () => {
  test('returns no errors for valid input', () => {
    expect(validateContact({ name: 'Sanskar', email: 'a@b.com', message: 'Hi' })).toEqual({});
  });
  test('flags all empty fields', () => {
    expect(Object.keys(validateContact({}))).toEqual(['name', 'email', 'message']);
  });
  test('flags whitespace-only values', () => {
    expect(validateContact({ name: '  ', email: 'a@b.com', message: ' ' })).toEqual({
      name: 'Name is required.',
      message: 'Message is required.',
    });
  });
  test('flags invalid email format', () => {
    expect(validateContact({ name: 'S', email: 'bad', message: 'm' }).email).toBe('Enter a valid email address.');
  });
});
