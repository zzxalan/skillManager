export function buildLocationSearchParams(locationValue: string): URLSearchParams {
  const hashIndex = locationValue.indexOf("#");
  const queryPart =
    hashIndex >= 0 ? locationValue.slice(locationValue.indexOf("?", hashIndex)) : locationValue;
  const queryIndex = queryPart.indexOf("?");
  const search = queryIndex >= 0 ? queryPart.slice(queryIndex) : "";
  return new URLSearchParams(search);
}
