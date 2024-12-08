<h1 align="center">
  Mafia Online API on Python
</h1>


<p align="center">This library for <a href="https://play.google.com/store/apps/details?id=com.tokarev.mafia">Mafia Online</a></p>

# Install
```
git clone https://github.com/unelected/zafiaonline.py.git
```

# Import and Auth
```python
import zafiaonline

Mafia = zafiaonline.Client()
Mafia.sign_in("email", "password")
```