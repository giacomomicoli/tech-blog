type RouteParams = Record<string, string | string[] | undefined>
type LocalePathFn = (route: string, locale?: string) => string

interface ResolveLocaleSwitchPathOptions {
  currentPath: string
  routeParams: RouteParams
  sameRoutePath: string
  fallbackPath: string
  targetLocale: string
  alternates?: Record<string, string>
}

function getSingleParam(value: string | string[] | undefined): string | null {
  if (typeof value === 'string' && value.length > 0) return value
  if (Array.isArray(value) && value.length > 0) return value[0] || null
  return null
}

export function stripLocalePrefix(path: string): string {
  const strippedPath = path.replace(/^\/[^/]+(?=\/|$)/, '')
  return strippedPath || '/'
}

export function getLocaleSwitchHref(currentPath: string, targetLocale: string, localePath: LocalePathFn): string {
  const normalizedPath = stripLocalePrefix(currentPath)

  if (
    normalizedPath.startsWith('/blog/')
    || normalizedPath.startsWith('/category/')
    || normalizedPath.startsWith('/tag/')
  ) {
    return localePath('/', targetLocale)
  }

  return localePath(normalizedPath, targetLocale)
}

export async function resolveLocaleSwitchPath({
  currentPath,
  routeParams,
  sameRoutePath,
  fallbackPath,
  targetLocale,
  alternates,
}: ResolveLocaleSwitchPathOptions): Promise<string> {
  const normalizedPath = stripLocalePrefix(currentPath)

  if (alternates?.[targetLocale]) {
    return alternates[targetLocale]
  }

  if (normalizedPath.startsWith('/blog/')) {
    return getSingleParam(routeParams.slug) ? fallbackPath : sameRoutePath
  }

  if (normalizedPath.startsWith('/category/')) {
    return getSingleParam(routeParams.name) ? fallbackPath : sameRoutePath
  }

  if (normalizedPath.startsWith('/tag/')) {
    return getSingleParam(routeParams.name) ? fallbackPath : sameRoutePath
  }

  return sameRoutePath
}
