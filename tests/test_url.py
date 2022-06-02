# stdlib
import os
import pathlib
import sys
from abc import ABC, abstractmethod
from ipaddress import IPv4Address
from typing import Type

# 3rd party
import pytest
from coincidence import count

# this package
from apeye_core import URL, Domain, URLPath


class MyPathLike(os.PathLike):

	def __fspath__(self):
		return "/python"


class TestURLPath:

	@pytest.mark.parametrize(
			"value, expected",
			[
					("/watch?v=NG21KWZSiok", '/'),
					("watch?v=NG21KWZSiok", ''),
					('', ''),
					("/programmes/b006qtlx/episodes/player", '/'),
					("/news", '/'),
					("news", ''),
					]
			)
	def test_drive_root_anchor(self, value: str, expected: str):
		# These were originally NotImplemented, but they weren't doing any harm and might be useful
		assert URLPath(value).drive == ''
		assert URLPath(value).root == expected
		assert URLPath(value).anchor == expected

	@pytest.mark.parametrize(
			"value, absolute",
			[
					(URLPath(), False),
					(URLPath(''), False),
					(URLPath('/'), True),
					(URLPath("/news"), True),
					(URLPath("news"), False),
					(URLPath("/programmes/b006qtlx"), True),
					(URLPath("programmes/b006qtlx"), False),
					(URLPath("/programmes/b006qtlx/episodes/player"), True),
					(URLPath("/watch?v=NG21KWZSiok"), True),
					(URLPath("watch?v=NG21KWZSiok"), False),
					]
			)
	def test_is_absolute(self, value: str, absolute: bool):
		# Was originally NotImplemented, but it might be useful
		assert URLPath(value).is_absolute() is absolute

	@pytest.mark.parametrize(
			"value", [
					"/watch?v=NG21KWZSiok",
					"watch?v=NG21KWZSiok",
					'',
					"/programmes/b006qtlx/episodes/player",
					]
			)
	def test_str(self, value):
		assert str(URLPath(value)) == value

	@pytest.mark.parametrize(
			"value, expects",
			[
					("/watch?v=NG21KWZSiok", "URLPath('/watch?v=NG21KWZSiok')"),
					("watch?v=NG21KWZSiok", "URLPath('watch?v=NG21KWZSiok')"),
					('', "URLPath('')"),
					("/programmes/b006qtlx/episodes/player", "URLPath('/programmes/b006qtlx/episodes/player')"),
					]
			)
	def test_repr(self, value, expects):
		assert repr(URLPath(value)) == expects

	@pytest.mark.parametrize("method", [URLPath().as_uri])
	def test_notimplemented(self, method):
		with pytest.raises(NotImplementedError):
			method()

	@pytest.mark.parametrize(
			"value, expects",
			[
					(URLPath() / "news", URLPath("news")),
					(URLPath('/') / "news", URLPath("/news")),
					(URLPath("/programmes") / "b006qtlx", URLPath("/programmes/b006qtlx")),
					("/programmes" / URLPath("b006qtlx"), URLPath("/programmes/b006qtlx")),
					]
			)
	def test_division(self, value, expects):
		assert value == expects
		assert isinstance(value, URLPath)

	@pytest.mark.parametrize(
			"value, expects",
			[
					(URLPath() / pathlib.PurePosixPath("news"), URLPath("news")),
					(URLPath() / URLPath("news"), URLPath("news")),
					(URLPath('/') / pathlib.PurePosixPath("news"), URLPath("/news")),
					(URLPath('/') / URLPath("news"), URLPath("/news")),
					(URLPath('/') / MyPathLike(), URLPath("/python")),
					(URLPath("/programmes") / pathlib.PurePosixPath("b006qtlx"), URLPath("/programmes/b006qtlx")),
					(URLPath("/programmes") / URLPath("b006qtlx"), URLPath("/programmes/b006qtlx")),
					pytest.param(
							pathlib.PurePosixPath("/programmes") / URLPath("b006qtlx"),
							URLPath("/programmes/b006qtlx"),
							marks=pytest.mark.xfail(reason="The type is taken from the left object.")
							),
					]
			)
	def test_division_pathlike(self, value, expects):
		assert value == expects
		assert isinstance(value, URLPath)

	@pytest.mark.parametrize(
			"value, expects",
			[
					(URLPath().joinpath("news"), URLPath("news")),
					(URLPath('/').joinpath("news"), URLPath("/news")),
					(URLPath("/programmes").joinpath("b006qtlx"), URLPath("/programmes/b006qtlx")),
					(
							URLPath("/programmes").joinpath("b006qtlx", "details"),
							URLPath("/programmes/b006qtlx/details")
							),
					]
			)
	def test_joinpath(self, value, expects):
		assert value == expects
		assert isinstance(value, URLPath)

	# pylint: disable=expression-not-assigned

	@count(100)
	def test_division_errors_number(self, count: int):
		if sys.version_info < (3, 8):
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not int"):
				URLPath() / count  # type: ignore[operator]
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not float"):
				URLPath() / float(count)  # type: ignore[operator]
		else:
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: 'URLPath' and 'int'"):
				URLPath() / count
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: 'URLPath' and 'float'"):
				URLPath() / float(count)

	@pytest.mark.parametrize("obj", [[], (), {}, set(), pytest.raises, ABC])
	def test_division_errors(self, obj):
		if sys.version_info < (3, 8):
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not .*"):
				URLPath() / obj
		else:
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: 'URLPath' and .*"):
				URLPath() / obj

	@pytest.mark.parametrize("obj", [1234, 12.34, [], (), {}, set(), pytest.raises, ABC])
	def test_rtruediv_typerror(self, obj):
		if sys.version_info < (3, 8):
			with pytest.raises(TypeError, match=r"expected str, bytes or os.PathLike object, not .*"):
				obj / URLPath()
		else:
			with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: .* and 'URLPath'"):
				obj / URLPath()

	# pylint: enable=expression-not-assigned

	@pytest.mark.parametrize(
			"base, other",
			[
					(URLPath("/news/sport"), "/news"),
					(URLPath("/news/sport"), URLPath("/news")),
					(URLPath("/news/sport"), pathlib.PurePosixPath("/news")),
					(URLPath("news/sport"), "news"),
					(URLPath("news/sport"), URLPath("news")),
					(URLPath("news/sport"), pathlib.PurePosixPath("news")),
					]
			)
	def test_relative_to(self, base: URLPath, other):
		assert base.relative_to(other) == URLPath("sport")
		assert isinstance(base.relative_to(other), URLPath)


class _TestURL(ABC):

	@property
	@abstractmethod
	def _class(self) -> Type:
		pass

	@pytest.mark.parametrize(
			"url, scheme, netloc, path",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes/player",
							"https",
							"www.bbc.co.uk",
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					(
							"www.bbc.co.uk/programmes/b006qtlx/episodes/player",
							'',
							"www.bbc.co.uk",
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					(
							"/programmes/b006qtlx/episodes/player",
							'',
							'',
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					(
							"//www.bbc.co.uk/programmes/b006qtlx/episodes/player",
							'',
							"www.bbc.co.uk",
							URLPath("/programmes/b006qtlx/episodes/player"),
							),
					]
			)
	def test_creation(self, url, scheme, netloc, path):
		url = self._class(url)
		assert url.scheme == scheme
		assert url.netloc == netloc
		assert url.path == path

	@pytest.mark.parametrize(
			"url",
			[
					"https://www.bbc.co.uk/programmes/b006qtlx/episodes/player",
					"www.bbc.co.uk/programmes/b006qtlx/episodes/player",
					"www.bbc.co.uk",
					"/programmes/b006qtlx/episodes/player",
					"programmes/b006qtlx/episodes/player",
					"https://127.0.0.1/programmes/b006qtlx/episodes/player",
					"ftp://127.0.0.1/programmes/b006qtlx/episodes/player",
					]
			)
	def test_str(self, url):
		assert str(self._class(url)) == url

	def test_division(self):
		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / "player"
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("/programmes/b006qtlx/episodes") / "player"
		assert value == self._class("/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("/programmes/b006qtlx/episodes") / "/news"
		assert value == self._class("/news")
		assert isinstance(value, self._class)

		value = self._class("www.bbc.co.uk/news")
		assert self._class("www.bbc.co.uk") / "news" == value
		assert isinstance(value, self._class)

		value = self._class("/news")
		assert self._class() / "news" == value
		assert isinstance(value, self._class)

	def test_division_pathlike(self):
		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / pathlib.PurePosixPath("player")
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / URLPath("player")
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / URL("player")
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / URL("/news")
		assert value == self._class("https://www.bbc.co.uk/news")
		assert isinstance(value, self._class)

		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes") / MyPathLike()
		assert value == self._class("https://www.bbc.co.uk/python")
		assert isinstance(value, self._class)

		value = self._class("/programmes/b006qtlx/episodes") / pathlib.PurePosixPath("player")
		assert value == self._class("/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("/programmes/b006qtlx/episodes") / URLPath("player")
		assert value == self._class("/programmes/b006qtlx/episodes/player")
		assert isinstance(value, self._class)

		value = self._class("www.bbc.co.uk/news")
		assert self._class("www.bbc.co.uk") / pathlib.PurePosixPath("news") == value
		assert isinstance(value, self._class)

		value = self._class("www.bbc.co.uk/news")
		assert self._class("www.bbc.co.uk") / URLPath("news") == value
		assert isinstance(value, self._class)

		value = self._class("/news")
		assert self._class() / pathlib.PurePosixPath("news") == value
		assert isinstance(value, self._class)

		value = self._class("/news")
		assert self._class() / URLPath("news") == value
		assert isinstance(value, self._class)

	@count(100)
	def test_division_number(self, count: int):
		assert (self._class() / count).parts[-1] == str(count)
		assert isinstance(self._class() / count, self._class)

		with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: '.*' and 'float'"):
			self._class() / float(count)  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize("obj", [[], (), {}, set(), pytest.raises, ABC])
	def test_division_errors(self, obj):
		with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: '.*' and .*"):
			self._class() / obj  # pylint: disable=expression-not-assigned

	@pytest.mark.parametrize("obj", [1234, 12.34, "abcdefg", [], (), {}, set(), pytest.raises, ABC])
	def test_rtruediv_typerror(self, obj):
		with pytest.raises(TypeError, match=r"unsupported operand type\(s\) for /: .* and '.*'"):
			obj / self._class()  # pylint: disable=expression-not-assigned

	def test_joinurl(self):
		value = self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes").joinurl("player")
		assert value == self._class("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player")

		value = self._class("/programmes/b006qtlx/episodes").joinurl("player")
		assert value == self._class("/programmes/b006qtlx/episodes/player")

		assert self._class("www.bbc.co.uk").joinurl("news") == self._class("www.bbc.co.uk/news")
		assert self._class().joinurl("news") == self._class("/news")

		assert self._class("www.bbc.co.uk").joinurl("news", "sport") == self._class("www.bbc.co.uk/news/sport")

		expected = self._class("www.bbc.co.uk/news/sport?que=ry")
		assert self._class("www.bbc.co.uk").joinurl("news#anchor", "sport?que=ry") == expected

		expected = self._class("www.bbc.co.uk/news/sport#anchor")
		assert self._class("www.bbc.co.uk").joinurl("news?que=ry", "sport#anchor") == expected

	def test_empty_url_operations(self):
		assert self._class().name == ''
		assert self._class().suffix == ''
		assert self._class().fqdn == ''
		assert self._class().stem == ''
		assert self._class().suffixes == []
		assert self._class().port is None

	@pytest.mark.parametrize(
			"url, name",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "episodes"),
					("www.bbc.co.uk", ''),
					("/programmes/b006qtlx/episodes", "episodes"),
					]
			)
	def test_name(self, url, name):
		assert self._class(url).name == name

	@pytest.mark.parametrize(
			"url, suffix",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", ''),
					("www.bbc.co.uk", ''),
					("/programmes/b006qtlx/episodes", ''),
					("https://imgs.xkcd.com/comics/workflow.png", ".png"),
					]
			)
	def test_suffix(self, url, suffix):
		assert self._class(url).suffix == suffix

	@pytest.mark.parametrize(
			"url, suffixes",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", []),
					("www.bbc.co.uk", []),
					("/programmes/b006qtlx/episodes", []),
					("https://imgs.xkcd.com/comics/workflow.png", [".png"]),
					(
							"https://github.com/domdfcoding/domdf_python_tools/releases/download/"
							"v0.4.8/domdf_python_tools-0.4.8.tar.gz", [".4", ".8", ".tar", ".gz"]
							),
					]
			)
	def test_suffixes(self, url, suffixes):
		assert self._class(url).suffixes == suffixes

	@pytest.mark.parametrize(
			"url, stem",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "episodes"),
					("www.bbc.co.uk", ''),
					("/programmes/b006qtlx/episodes", "episodes"),
					("https://imgs.xkcd.com/comics/workflow.png", "workflow"),
					(
							"https://github.com/domdfcoding/domdf_python_tools/releases/download/v0.4.8/domdf_python_tools-0.4.8.tar.gz",
							"domdf_python_tools-0.4.8.tar"
							),
					]
			)
	def test_stem(self, url, stem):
		assert self._class(url).stem == stem

	def test_with_name_errors(self):
		with pytest.raises(ValueError, match=r"URLPath\(''\) has an empty name"):
			self._class("www.bbc.co.uk").with_name("bar")

		with pytest.raises(ValueError, match=r"URLPath\(''\) has an empty name"):
			self._class().with_name("bar")

	@pytest.mark.parametrize(
			"url, expected, name",
			[(
					"https://www.bbc.co.uk/programmes/b006qtlx/episodes",
					"https://www.bbc.co.uk/programmes/b006qtlx/foo",
					"foo"
					),
				(
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry",
						"https://www.bbc.co.uk/programmes/b006qtlx/foo",
						"foo"
						),
				(
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes#fragment",
						"https://www.bbc.co.uk/programmes/b006qtlx/foo",
						"foo"
						),
				(
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry#fragment",
						"https://www.bbc.co.uk/programmes/b006qtlx/foo",
						"foo"
						), ("/programmes/b006qtlx/episodes", "/programmes/b006qtlx/foo", "foo"),
				("https://imgs.xkcd.com/comics/workflow.png", "https://imgs.xkcd.com/comics/baz", "baz")]
			)
	def test_with_name(self, url: str, expected: str, name: str):
		assert self._class(url).with_name(name) == self._class(expected)

	@pytest.mark.parametrize(
			"url, expected",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes",
							"https://www.bbc.co.uk/programmes/b006qtlx/foo",
							),
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry",
							"https://www.bbc.co.uk/programmes/b006qtlx/foo?que=ry",
							),
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes#fragment",
							"https://www.bbc.co.uk/programmes/b006qtlx/foo#fragment",
							),
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry#fragment",
							"https://www.bbc.co.uk/programmes/b006qtlx/foo?que=ry#fragment",
							),
					]
			)
	def test_with_name_inherit(self, url: str, expected: str):
		assert self._class(url).with_name("foo", inherit=True) == self._class(expected)

	@pytest.mark.parametrize(
			"url, expected, suffix",
			[(
					"https://www.bbc.co.uk/programmes/b006qtlx/episodes",
					"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo",
					".foo"
					),
				(
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry",
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo",
						".foo"
						),
				(
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes#fragment",
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo",
						".foo"
						),
				(
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry#fragment",
						"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo",
						".foo"
						), ("/programmes/b006qtlx/episodes", "/programmes/b006qtlx/episodes.foo", ".foo"),
				("https://imgs.xkcd.com/comics/workflow.png", "https://imgs.xkcd.com/comics/workflow.baz", ".baz")]
			)
	def test_with_suffix(self, url: str, expected: str, suffix: str):
		assert self._class(url).with_suffix(suffix) == self._class(expected)

	@pytest.mark.parametrize(
			"url, expected",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes",
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo",
							),
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry",
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo?que=ry",
							),
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes#fragment",
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo#fragment",
							),
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes?que=ry#fragment",
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes.foo?que=ry#fragment",
							),
					]
			)
	def test_with_suffix_inherit(self, url: str, expected: str):
		assert self._class(url).with_suffix(".foo", inherit=True) == self._class(expected)

	@pytest.mark.parametrize(
			"url, parent",
			[
					(
							"https://www.bbc.co.uk/programmes/b006qtlx/episodes",
							"https://www.bbc.co.uk/programmes/b006qtlx"
							),
					("/programmes/b006qtlx/episodes", "/programmes/b006qtlx"),
					("https://imgs.xkcd.com/comics/workflow.png", "https://imgs.xkcd.com/comics"),
					]
			)
	def test_parent(self, url, parent):
		assert self._class(url).parent == self._class(parent)

	@pytest.mark.parametrize(
			"url, fqdn",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "www.bbc.co.uk"),
					("www.bbc.co.uk", "www.bbc.co.uk"),
					("/programmes/b006qtlx/episodes", ''),
					("https://imgs.xkcd.com/comics/workflow.png", "imgs.xkcd.com"),
					]
			)
	def test_fqdn(self, url, fqdn):
		assert self._class(url).fqdn == fqdn

	@pytest.mark.parametrize(
			"url, subdomain, domain, suffix, ipv4",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", "www", "bbc", "co.uk", None),
					("/programmes/b006qtlx/episodes", '', '', '', None),
					("https://www.bbc.co.uk", "www", "bbc", "co.uk", None),
					("ftp://127.0.0.1/download.zip", '', "127.0.0.1", '', IPv4Address("127.0.0.1")),
					]
			)
	def test_domain(self, url, subdomain, domain, suffix, ipv4):
		assert isinstance(self._class(url).domain, Domain)
		assert self._class(url).domain.subdomain == subdomain
		assert self._class(url).domain.domain == domain
		assert self._class(url).domain.suffix == suffix
		assert self._class(url).domain.ipv4 == ipv4

	@pytest.mark.parametrize(
			"url, port",
			[
					("https://www.bbc.co.uk/programmes/b006qtlx/episodes", None),
					("https://www.bbc.co.uk:80/programmes/b006qtlx/episodes", 80),
					("https://www.bbc.co.uk:8080/programmes/b006qtlx/episodes", 8080),
					("https://www.bbc.co.uk:443/programmes/b006qtlx/episodes", 443),
					("www.bbc.co.uk", None),
					("www.bbc.co.uk:80", 80),
					("www.bbc.co.uk:8080", 8080),
					("www.bbc.co.uk:443", 443),
					("/programmes/b006qtlx/episodes", None),
					]
			)
	def test_port(self, url, port):
		assert self._class(url).port == port

	@pytest.mark.parametrize(
			"url, expects",
			[
					("bbc.co.uk/news", "bbc.co.uk/news"),
					("https://bbc.co.uk/news", "bbc.co.uk/news"),
					("https://www.bbc.co.uk/news", "www.bbc.co.uk/news"),
					]
			)
	def test_cast_to_pathlib(self, url, expects):
		assert pathlib.Path(self._class(url)) == pathlib.Path(expects)

	@pytest.mark.parametrize(
			"url, expects",
			[
					("bbc.co.uk/news", "bbc.co.uk/news"),
					("https://bbc.co.uk/news", "bbc.co.uk/news"),
					("https://www.bbc.co.uk/news", "www.bbc.co.uk/news"),
					]
			)
	def test_fspath(self, url, expects):
		assert self._class(url).__fspath__() == expects
		assert os.fspath(self._class(url)) == expects

	def test_hash(self):
		assert hash(self._class("bbc.co.uk")) == hash(self._class("bbc.co.uk"))
		assert hash(self._class("bbc.co.uk/news")) != hash(self._class("bbc.co.uk"))
		assert {self._class("bbc.co.uk"), hash(self._class("bbc.co.uk/news"))}

	@pytest.mark.parametrize(
			"url, parts",
			[
					(
							"https://hub.docker.com/r/tobix/pywine/dockerfile",
							("https", "hub", "docker", "com", 'r', "tobix", "pywine", "dockerfile")
							),
					]
			)
	def test_parts(self, url, parts):
		assert self._class(url).parts == parts

	def test_parents(self):
		assert self._class("https://hub.docker.com/r/tobix/pywine/dockerfile").parents == (
				self._class("https://hub.docker.com/r/tobix/pywine"),
				self._class("https://hub.docker.com/r/tobix"),
				self._class("https://hub.docker.com/r"),
				self._class("https://hub.docker.com/"),
				)

	def test_notimplemented_eq(self):
		assert URL() != 7
		assert URL() != 3.14142
		assert URL() != 'a'
		assert URL() != [7, 'a', 3.14142]
		assert URL() != (7, 'a', 3.14142)
		assert URL() != {7, 'a', 3.14142}
		assert URL() != {"int": 7, "str": 'a', "float": 3.14142}

	def test_from_url(self):
		url = URL("bbc.co.uk")
		assert self._class(url) == url

	def test_with_query(self):
		url = self._class("https://api.github.com/user/domdfcoding/repos?page=2&per_page=50")
		assert url.query == {"page": ['2'], "per_page": ["50"]}

		url = self._class("https://api.github.com/user/domdfcoding/repos?name=bob")
		assert url.query == {"name": ["bob"]}

		url = self._class("https://api.github.com/user/domdfcoding/repos")
		assert url.query == {}

		url = self._class("https://api.github.com?foo=bar")
		assert url.query == {"foo": ["bar"]}
		assert (url / "users").query == {}

	def test_with_fragment(self):
		url = self._class("https://api.github.com/user/domdfcoding/repos#footer")
		assert url.fragment == "footer"

		url = self._class("https://api.github.com/user/domdfcoding/repos")
		assert url.fragment is None

		url = self._class("https://api.github.com#footer")
		assert url.fragment == "footer"
		assert (url / "users").fragment is None

	def test_relative_to(self):
		expected = URLPath("domdfcoding")
		assert self._class("https://github.com/domdfcoding").relative_to(URL("https://github.com")) == expected

		expected = URLPath("football")
		assert self._class("https://www.bbc.co.uk:443/news/sport/football").relative_to("/news/sport") == expected
		assert self._class("https://www.bbc.co.uk:443/news/sport/football").relative_to(
				URLPath("/news/sport")
				) == expected

		with pytest.raises(ValueError, match="'URL.relative_to' cannot be used with relative URLPath objects"):
			self._class("https://www.bbc.co.uk:443/news/sport/football").relative_to(URLPath("news/sport"))

		with pytest.raises(ValueError, match=".* does not start with .*"):
			self._class("https://github.com/domdfcoding").relative_to(URL("https://bbc.co.uk/news"))

		with pytest.raises(ValueError, match=".* does not start with .*"):
			self._class("https://www.bbc.co.uk:443/news/sport").relative_to(URL("https://bbc.co.uk/news"))

		# Perhaps not quite what was intended
		match = r".*URL\('https://bbc.co.uk/news/sport/football(/)?'\) does not start with .*URL\('news/sport'\)"
		with pytest.raises(ValueError, match=match):
			self._class("https://bbc.co.uk/news/sport/football").relative_to("news/sport")

		the_url = self._class("https://github.com/domdfcoding")
		assert the_url.path == URLPath("/domdfcoding")
		the_url.path = URLPath("domdfcoding")
		assert the_url.path == URLPath("domdfcoding")
		assert the_url.relative_to(URL("https://github.com")) == URLPath("domdfcoding")

		# Should be case insensitive (NOT case folded) per RFC 4343
		expected = URLPath("domdfcoding")
		url = self._class("https://github.com/domdfcoding")
		assert url.relative_to(self._class("https://GitHub.COM")) == expected

	def test_ordering(self):
		# f comes before t
		football = self._class("https://bbc.co.uk:443/news/sport/football")
		tennis = self._class("https://bbc.co.uk:443/news/sport/tennis")
		assert football < tennis
		assert football <= tennis
		assert tennis > football
		assert tennis >= football
		assert sorted([tennis, football]) == [football, tennis]

		# port number is sorted before path
		tennis = self._class("https://bbc.co.uk:80/news/sport/tennis")
		assert tennis < self._class("https://bbc.co.uk:443/news/sport/football")
		assert tennis <= self._class("https://bbc.co.uk:443/news/sport/football")
		assert football > tennis
		assert football >= tennis

		# scheme is sorted before path
		tennis = self._class("http://bbc.co.uk/news/sport/tennis")
		assert tennis < self._class("https://bbc.co.uk/news/sport/football")
		assert tennis <= self._class("https://bbc.co.uk/news/sport/football")
		assert self._class("https://bbc.co.uk/news/sport/football") > tennis
		assert self._class("https://bbc.co.uk/news/sport/football") >= tennis

		# Empty subdomain comes first
		tennis = self._class("https://bbc.co.uk/news/sport/tennis")
		assert tennis < self._class("https://news.bbc.co.uk/sport/tennis")
		assert tennis <= self._class("https://news.bbc.co.uk/sport/tennis")
		assert self._class("https://news.bbc.co.uk/sport/tennis") > tennis
		assert self._class("https://news.bbc.co.uk/sport/tennis") >= tennis

	@pytest.mark.parametrize("other_class", [URL])
	def test_ordering_other_classes(self, other_class):
		# f comes before t
		football = "https://bbc.co.uk:443/news/sport/football"
		tennis = "https://bbc.co.uk:443/news/sport/tennis"
		assert self._class(football) < other_class(tennis)
		assert self._class(football) <= other_class(tennis)
		assert self._class(tennis) > other_class(football)
		assert self._class(tennis) >= other_class(football)
		assert sorted([self._class(tennis), other_class(football)]) == [self._class(football), self._class(tennis)]

		# port number is sorted before path
		tennis = "https://bbc.co.uk:80/news/sport/tennis"
		assert self._class(tennis) < other_class(football)
		assert self._class(tennis) <= other_class(football)
		assert self._class(football) > other_class(tennis)
		assert self._class(football) >= other_class(tennis)

		# scheme is sorted before path
		tennis = "http://bbc.co.uk/news/sport/tennis"
		assert self._class(tennis) < other_class("https://bbc.co.uk/news/sport/football")
		assert self._class(tennis) <= other_class("https://bbc.co.uk/news/sport/football")
		assert self._class("https://bbc.co.uk/news/sport/football") > other_class(tennis)
		assert self._class("https://bbc.co.uk/news/sport/football") >= other_class(tennis)

		# Empty subdomain comes first
		tennis = "https://bbc.co.uk/news/sport/tennis"

		assert self._class(tennis) < other_class("https://news.bbc.co.uk/sport/tennis")
		assert self._class(tennis) <= other_class("https://news.bbc.co.uk/sport/tennis")
		assert self._class("https://news.bbc.co.uk/sport/tennis") > other_class(tennis)
		assert self._class("https://news.bbc.co.uk/sport/tennis") >= other_class(tennis)


class TestURL(_TestURL):

	_class = URL

	@pytest.mark.parametrize(
			"url, expects",
			[
					(
							URL("https://www.bbc.co.uk/programmes/b006qtlx/episodes/player"),
							"URL('https://www.bbc.co.uk/programmes/b006qtlx/episodes/player')"
							),
					(
							URL("www.bbc.co.uk/programmes/b006qtlx/episodes/player"),
							"URL('www.bbc.co.uk/programmes/b006qtlx/episodes/player')"
							),
					(URL("www.bbc.co.uk"), "URL('www.bbc.co.uk')"),
					(URL("/programmes/b006qtlx/episodes/player"), "URL('/programmes/b006qtlx/episodes/player')"),
					(URL("programmes/b006qtlx/episodes/player"), "URL('programmes/b006qtlx/episodes/player')"),
					(
							URL("https://127.0.0.1/programmes/b006qtlx/episodes/player"),
							"URL('https://127.0.0.1/programmes/b006qtlx/episodes/player')"
							),
					(
							URL("ftp://127.0.0.1/programmes/b006qtlx/episodes/player"),
							"URL('ftp://127.0.0.1/programmes/b006qtlx/episodes/player')"
							),
					]
			)
	def test_repr(self, url, expects):
		assert repr(url) == expects

	def test_isinstance(self):
		assert isinstance(URL(), URL)
		assert isinstance(URL(), os.PathLike)

	def test_equality(self):
		assert URL() == URL()
		assert URL("bbc.co.uk") == URL("bbc.co.uk")
		assert URL("https://bbc.co.uk") == URL("https://bbc.co.uk")
		assert URL("bbc.co.uk/news") == URL("bbc.co.uk/news")

		assert URL("bbc.co.uk") != URL("bbc.co.uk/news")
		assert URL("bbc.co.uk") != URL("http://bbc.co.uk/news")
		assert URL("bbc.co.uk") != URL("http://bbc.co.uk")

	def test_strict_equality(self):
		assert URL().strict_compare(URL())
		assert URL("bbc.co.uk").strict_compare(URL("bbc.co.uk"))
		assert URL("bbc.co.uk#fragment").strict_compare(URL("bbc.co.uk#fragment"))
		assert URL("bbc.co.uk?que=ry").strict_compare(URL("bbc.co.uk?que=ry"))
		assert URL("bbc.co.uk?que=ry#fragment").strict_compare(URL("bbc.co.uk?que=ry#fragment"))
		assert URL("https://bbc.co.uk").strict_compare(URL("https://bbc.co.uk"))
		assert URL("https://bbc.co.uk#fragment").strict_compare(URL("https://bbc.co.uk#fragment"))
		assert URL("https://bbc.co.uk?que=ry").strict_compare(URL("https://bbc.co.uk?que=ry"))
		assert URL("https://bbc.co.uk?que=ry#fragment").strict_compare(URL("https://bbc.co.uk?que=ry#fragment"))
		assert URL("bbc.co.uk/news").strict_compare(URL("bbc.co.uk/news"))
		assert URL("bbc.co.uk/news#fragment").strict_compare(URL("bbc.co.uk/news#fragment"))
		assert URL("bbc.co.uk/news?que=ry").strict_compare(URL("bbc.co.uk/news?que=ry"))
		assert URL("bbc.co.uk/news?que=ry#fragment").strict_compare(URL("bbc.co.uk/news?que=ry#fragment"))

		assert not URL("bbc.co.uk").strict_compare(URL("bbc.co.uk/news"))
		assert not URL("bbc.co.uk#fragment").strict_compare(URL("bbc.co.uk/news"))
		assert not URL("bbc.co.uk#fragment").strict_compare(URL("bbc.co.uk"))
		assert not URL("bbc.co.uk?que=ry").strict_compare(URL("bbc.co.uk/news"))
		assert not URL("bbc.co.uk?que=ry").strict_compare(URL("bbc.co.uk"))
		assert not URL("bbc.co.uk?que=ry").strict_compare(URL("bbc.co.uk/news#fragment"))
		assert not URL("bbc.co.uk?que=ry").strict_compare(URL("bbc.co.uk#fragment"))
		assert not URL("bbc.co.uk").strict_compare(URL("http://bbc.co.uk/news"))
		assert not URL("bbc.co.uk").strict_compare(URL("http://bbc.co.uk"))


def test_domain_class():
	d = Domain("docs", "python", "org")
	assert d.subdomain == "docs"
	assert d.domain == "python"
	assert d.suffix == "org"
	assert d.fqdn == "docs.python.org"
	assert d.registered_domain == "python.org"
	assert d.ipv4 is None
	assert repr(d) == "Domain(subdomain='docs', domain='python', suffix='org')"

	iv4d = Domain(subdomain='', domain="127.0.0.1", suffix='')
	assert iv4d.subdomain == ''
	assert iv4d.domain == "127.0.0.1"
	assert iv4d.suffix == ''
	assert iv4d.fqdn == ''
	assert iv4d.registered_domain == ''
	assert iv4d.ipv4 == IPv4Address("127.0.0.1")
	assert repr(iv4d) == "Domain(subdomain='', domain='127.0.0.1', suffix='')"
