from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from pathlib import Path
import random

class BingRewardsAutomator:
    def __init__(self):
        self.driver = None
        self.completed_tasks = []
        self.failed_tasks = []
        self.total_points = 0
        self.start_time = datetime.now()
        self.driver_path = Path(__file__).resolve().parent / "msedgedriver.exe"
        self.wait_timeout = 15
        
    def setup_driver(self):
        """Initialize the Edge WebDriver with recovery options"""
        try:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
            
            edge_options = Options()
            edge_options.add_argument("--start-maximized")
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_argument("--disable-crash-reporter")
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            service = Service(str(self.driver_path))
            self.driver = webdriver.Edge(service=service, options=edge_options)
            print("[✓] Edge WebDriver initialized")
            return True
        except Exception as e:
            print(f"[✗] Failed to setup driver: {e}")
            return False
        
    def navigate_to_rewards(self):
        """Navigate to the Bing Rewards points breakdown page"""
        try:
            url = "https://rewards.bing.com/"
            self.driver.get(url)
            print(f"[✓] Navigating to {url}")
            sleep(5)
            return True
        except Exception as e:
            print(f"[✗] Failed to navigate: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present"""
        if timeout is None:
            timeout = self.wait_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def get_incomplete_tasks(self):
        """Find all incomplete tasks on the page"""
        try:
            self.wait_for_element(By.TAG_NAME, "div")
            sleep(3)
            
            # XPath patterns to find incomplete tasks
            xpath_patterns = [
                "//span[@aria-label='Points you will earn' and not(contains(@class, 'Lock'))]/../../../..",
                "//a[contains(@class, 'ds-card-sec')]//*[contains(@aria-label, 'Points in progress')]/../../../.."
            ]

            all_elements = []
            for pattern in xpath_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    all_elements.extend(elements)
                except Exception:
                    continue
            
            # Remove duplicates
            unique_elements = list(dict.fromkeys(all_elements))
            
            incomplete_tasks = []
            for idx, element in enumerate(unique_elements):
                try:
                    aria_label = element.get_attribute("aria-label") or ""
                    # Skip frozen/locked tasks
                    if "locked" in aria_label.lower() or "frozen" in aria_label.lower() or "disabled" in aria_label.lower():
                        print(f"[⊘] Skipping frozen/locked task: {aria_label[:50]}")
                        continue
                    
                    if "Points you will earn" in aria_label or "Points in progress" in aria_label or "earn" in aria_label.lower():
                        # Prefer explicit "Search on Bing" titles when aria-label mentions searching
                        aria_lower = aria_label.lower()
                        if "search on bing" in aria_lower:
                            title_text = "Search on Bing"
                        else:
                            # Preserve existing behavior: use text before first comma, otherwise a Task fallback
                            if "," in aria_label:
                                first = aria_label.split(",")[0].strip()
                                title_text = first if first else f"Task {idx+1}"
                            else:
                                title_text = f"Task {idx+1}"

                        # V3: Don't cache WebElement to avoid stale references
                        # Store enough info to re-fetch fresh element per task
                        task_info = {
                            "aria_label": aria_label,
                            "index": idx,
                            "title": title_text
                        }
                        incomplete_tasks.append(task_info)
                        print(f"[•] Found task {idx+1}: {task_info['title']}")
                except Exception:
                    continue
            
            return incomplete_tasks
        except Exception as e:
            print(f"[✗] Error getting incomplete tasks: {e}")
            return []
    
    def extract_points(self, aria_label):
        """Extract points value from aria-label"""
        try:
            parts = aria_label.split()
            for part in parts:
                if part.isdigit():
                    return int(part)
        except:
            pass
        return 0
    
    def extract_search_keywords(self, aria_label):
        """Extract intelligent search keywords from aria-label text"""
        label_lower = aria_label.lower()
        
        # Switch-case patterns: keyword triggers -> extraction logic
        # Pattern: (trigger_phrase, extraction_function)
        search_patterns = [
            ("lyrics", lambda: self._extract_lyrics_search(aria_label)),
            ("weather", lambda: self._extract_weather_search(aria_label)),
            ("recipe", lambda: self._extract_recipe_search(aria_label)),
            ("how to", lambda: self._extract_how_to_search(aria_label)),
            ("best", lambda: self._extract_best_search(aria_label)),
            ("find", lambda: self._extract_find_search(aria_label)),
            ("savings", lambda: self._extract_savings_search(aria_label)),
            ("flights", lambda: self._extract_flights_search(aria_label)),
            ("parking", lambda: self._extract_parking_search(aria_label)),
            ("flower", lambda: self._extract_flower_search(aria_label)),
            ("streaming", lambda: self._extract_streaming_search(aria_label)),
            ("events", lambda: self._extract_events_search(aria_label)),
        ]
        
        for trigger, extractor in search_patterns:
            if trigger in label_lower:
                keyword = extractor()
                if keyword:
                    return keyword
        
        # Fallback: extract text between commas (description)
        fallback = self._extract_fallback_search(aria_label)
        if fallback:
            return fallback
        
        # No patterns matched - return special value to indicate "just click, no search"
        return "__JUST_CLICK__"
    
    def _extract_lyrics_search(self, text):
        """Extract lyrics search: 'lyrics of your favorite X' -> 'lyrics of [Popular Song]'"""
        # Example: "Learn song lyrics" -> search "lyrics of Titanic"
        if "lyrics" in text.lower():
            popular_songs = ["Titanic", "Bohemian Rhapsody", "Imagine", "Let It Be", "Hotel California"]
            return f"lyrics of {random.choice(popular_songs)}"
        return None
    
    def _extract_weather_search(self, text):
        """Extract weather search: 'weather for X' -> 'weather [city]'"""
        if "weather" in text.lower():
            cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
            return f"weather {random.choice(cities)}"
        return None
    
    def _extract_recipe_search(self, text):
        """Extract recipe search: 'recipe for X' -> 'recipe [dish]'"""
        if "recipe" in text.lower():
            recipes = ["chocolate cake", "pasta carbonara", "chicken soup", "tiramisu"]
            return f"recipe {random.choice(recipes)}"
        return None
    
    def _extract_how_to_search(self, text):
        """Extract how-to search: 'how to X' -> 'how to [action]'"""
        if "how to" in text.lower():
            actions = ["tie a tie", "make coffee", "meditate", "cook steak"]
            return f"how to {random.choice(actions)}"
        return None
    
    def _extract_best_search(self, text):
        """Extract best search: 'best X' -> 'best [item]'"""
        if "best" in text.lower():
            items = ["restaurants near me", "books of 2026", "hiking trails", "laptops"]
            return f"best {random.choice(items)}"
        return None
    
    def _extract_find_search(self, text):
        """Extract find search: 'find X' -> 'find [thing]'"""
        if "find" in text.lower():
            things = ["hotels", "flights", "car rentals", "events"]
            return f"find {random.choice(things)}"
        return None

    def _extract_savings_search(self, text):
        """Extract savings search: 'savings X' -> 'savings [offer]'"""
        if "savings" in text.lower():
            offers = ["credit cards", "account options", "checking account options", "retirement"]
            return f"savings {random.choice(offers)}"
        return None

    def _extract_events_search(self, text):
        """Extract events search: 'events in X' -> 'events [city]'"""
        if "events" in text.lower():
            cities = ["Near me", "New York", "London", "Tokyo", "Paris", "Sydney"]
            return f"events {random.choice(cities)}"
        return None

    def _extract_flights_search(self, text):
        """Extract flights search: 'flights from X to Y' -> 'flights [origin] to [destination]'"""
        if "flights" in text.lower():
            origins = ["New York", "London", "Tokyo", "Paris", "Sydney"]
            destinations = ["Los Angeles", "Berlin", "Osaka", "Rome", "Melbourne"]
            return f"flights {random.choice(origins)} to {random.choice(destinations)}"
        return None

    def _extract_streaming_search(self, text):
        """Extract streaming search: 'streaming X' -> 'streaming [service]'"""
        if "streaming" in text.lower():
            services = ["Netflix", "Amazon Prime", "Hulu", "Disney+", "HBO Max"]
            return f"streaming {random.choice(services)} bundles"
        return None
        return None
    def _extract_parking_search(self, text):
        """Extract parking search: 'parking in X' -> 'parking [city]'"""
        if "parking" in text.lower():
            cities = ["Near airport", "New York", "London", "Tokyo", "Paris", "Sydney"]
            return f"parking {random.choice(cities)}"
        return None


    def _extract_flower_search(self, text):
        """Extract flower search: 'flowers in X' -> 'flowers [city]'"""
        if "flowers" in text.lower():
            cities = ["delivery Near me", "New York", "London", "Tokyo", "Paris", "Sydney"]
            return f"flowers {random.choice(cities)}"
        return None


    def _extract_fallback_search(self, text):
        """Fallback: extract description part (between first two commas) as search term"""
        parts = text.split(",")
        if len(parts) >= 2:
            # Use the description part (usually between title and points)
            description = parts[1].strip()
            # Return first few words as search term
            words = description.split()[:4]
            return " ".join(words) if words else None
        return None
    
    def perform_search_task(self, search_count=3, search_keywords=None):
        """Perform search-based rewards"""
        try:
            print(f"[→] Performing search task ({search_count} searches)...")
            
            # Use provided keywords or fall back to NLTK
            if search_keywords:
                keywords_to_use = search_keywords if isinstance(search_keywords, list) else [search_keywords]
            else:
                import nltk
                nltk.download('words', quiet=True)
                from nltk.corpus import words as nltk_words
                keywords_to_use = [random.choice(nltk_words.words()) for _ in range(search_count)]
            
            for i in range(min(search_count, len(keywords_to_use))):
                try:
                    if not self.driver:
                        print("[⚠] Browser disconnected, cannot continue searches")
                        break
                    
                    search_term = keywords_to_use[i] if i < len(keywords_to_use) else random.choice(keywords_to_use)
                    search_input = self.wait_for_element(By.NAME, "q", timeout=10)
                    
                    if search_input:
                        search_input.clear()
                        search_input.send_keys(search_term)
                        search_input.send_keys(Keys.RETURN)
                        sleep(6)
                        print(f"  [{i+1}/{search_count}] Searched for: {search_term}")
                    else:
                        print(f"[⚠] Could not find search input")
                        break
                except WebDriverException as e:
                    print(f"[⚠] WebDriver error during search {i+1}: {str(e)[:100]}")
                    return False
                except Exception as e:
                    print(f"[⚠] Error during search {i+1}: {e}")
                    continue
                    
            return True
        except Exception as e:
            print(f"[✗] Error in search task: {e}")
            return False
    
    def get_fresh_task_element(self, aria_label):
        """
        V3 Approach: Re-fetch fresh element from DOM using aria-label.
        Avoids stale element exceptions by always querying current state.
        """
        try:
            # Try to find element by exact aria-label (most reliable)
            xpath = f"//*[@aria-label='{aria_label}']"
            element = self.wait_for_element(By.XPATH, xpath, timeout=5)
            if element:
                return element
            
            # Fallback: search by partial aria-label
            partial_xpath = f"//*[contains(@aria-label, '{aria_label.split(',')[0].strip()}')]"
            element = self.wait_for_element(By.XPATH, partial_xpath, timeout=5)
            return element
        except Exception as e:
            print(f"[⚠] Could not re-fetch element for '{aria_label[:40]}...': {e}")
            return None
    
    def handle_task(self, task_info):
        """Handle completion of a single task"""
        try:
            aria_label = task_info.get("aria_label", "")
            title = task_info.get("title", "Unknown Task")
            points = self.extract_points(aria_label)
            
            print(f"\n[▶] Processing task: {title}")
            print(f"    Points available: {points}")
            
            # V3: Re-fetch fresh element from DOM to avoid stale references
            element = self.get_fresh_task_element(aria_label)
            if not element:
                print(f"[✗] Could not find task element")
                return False
            
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                sleep(2)
                
                # Try clicking
                try:
                    element.click()
                except:
                    # Retry: refresh element reference and try again
                    element = self.get_fresh_task_element(aria_label)
                    if element:
                        clickable = element.find_element(By.TAG_NAME, "button") or \
                                   element.find_element(By.TAG_NAME, "a")
                        clickable.click()
                    else:
                        raise Exception("Element not found after retry")
            except WebDriverException as e:
                print(f"[⚠] Browser error: {str(e)[:100]}")
                return False
            
            original_window = self.driver.current_window_handle
            sleep(3)
            
            all_windows = self.driver.window_handles
            if len(all_windows) > 1:
                new_window = [w for w in all_windows if w != original_window][0]
                self.driver.switch_to.window(new_window)
                sleep(3)
                
                current_url = self.driver.current_url
                if "bing.com" in current_url or "search" in current_url.lower():
                    print(f"    [→] Detected search task")
                    # Extract intelligent search keywords from aria-label
                    search_keywords = self.extract_search_keywords(aria_label)
                    if search_keywords == "__JUST_CLICK__":
                        print(f"    [→] No search pattern matched - just clicking element")
                        sleep(8)  # Wait for page action to complete
                    elif search_keywords:
                        print(f"    [→] Extracted search term: {search_keywords}")
                        self.perform_search_task(search_count=2, search_keywords=search_keywords)
                    else:
                        print(f"    [→] No keywords extracted - performing random searches")
                        self.perform_search_task(search_count=2)
                else:
                    print(f"    [→] Engagement task detected")
                    sleep(10)
                
                try:
                    self.driver.close()
                    self.driver.switch_to.window(original_window)
                    sleep(2)
                except:
                    pass
            else:
                print(f"    [→] Page action task")
                sleep(8)
            
            # Try to verify completion
            try:
                self.driver.refresh()
                sleep(2)
                completed_check = self.driver.find_elements(
                    By.XPATH, 
                    f"//*[contains(@aria-label, '{title}') and contains(@aria-label, 'earned')]"
                )
                if completed_check:
                    print(f"[✓] Task completed: {title} ({points} points)")
                    self.completed_tasks.append({
                        "title": title,
                        "points": points,
                        "status": "completed"
                    })
                    self.total_points += points
                    return True
                else:
                    print(f"[?] Task possibly completed: {title}")
                    self.completed_tasks.append({
                        "title": title,
                        "points": points,
                        "status": "possibly_completed"
                    })
                    return True
            except WebDriverException:
                print(f"[!] Verification skipped due to browser state")
                return True
                
        except WebDriverException as e:
            print(f"[✗] WebDriver error: {str(e)[:100]}")
            return False
        except Exception as e:
            print(f"[✗] Error handling task: {e}")
            self.failed_tasks.append({
                "title": task_info.get("title", "Unknown"),
                "error": str(e)[:100]
            })
            return False
    
    def run(self):
        """Main execution flow with retry logic"""
        try:
            if not self.setup_driver():
                return
            
            if not self.navigate_to_rewards():
                return
            
            # First pass: process all discovered tasks
            incomplete_tasks = self.get_incomplete_tasks()
            
            if not incomplete_tasks:
                print("\n[!] No incomplete tasks found")
                self.generate_summary()
                return
            
            print(f"\n[•] Found {len(incomplete_tasks)} incomplete task(s)\n")
            
            skipped_tasks = []
            for idx, task in enumerate(incomplete_tasks, 1):
                print(f"\n{'='*60}")
                print(f"Task {idx}/{len(incomplete_tasks)}")
                print(f"{'='*60}")
                
                if not self.handle_task(task):
                    print(f"[⚠] Task failed, will retry in second pass...")
                    skipped_tasks.append(task)
                
                sleep(2)
            
            # Second pass: retry any failed tasks
            if skipped_tasks:
                print(f"\n[→] Retrying {len(skipped_tasks)} failed task(s) after 3 seconds...\n")
                sleep(3)
                
                for idx, task in enumerate(skipped_tasks, 1):
                    print(f"\n{'='*60}")
                    print(f"Retry {idx}/{len(skipped_tasks)}")
                    print(f"{'='*60}")
                    
                    if not self.handle_task(task):
                        print(f"[⚠] Retry failed, skipping task")
                    
                    sleep(2)
            
            self.generate_summary()
            
            # Check for any remaining incomplete tasks
            self.check_remaining_tasks()
            
        except Exception as e:
            print(f"[✗] Fatal error: {e}")
            self.generate_summary()
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
    
    def generate_summary(self):
        """Generate and display completion summary"""
        duration = datetime.now() - self.start_time
        duration_str = f"{duration.seconds // 60}m {duration.seconds % 60}s"
        
        print("\n" + "="*60)
        print("BING REWARDS TASK COMPLETION SUMMARY")
        print("="*60)
        print(f"\nSession Duration: {duration_str}")
        print(f"Total Tasks Processed: {len(self.completed_tasks) + len(self.failed_tasks)}")
        print(f"Successfully Completed: {len(self.completed_tasks)}")
        print(f"Failed/Skipped: {len(self.failed_tasks)}")
        print(f"Total Points Earned: {self.total_points}")
        
        if self.completed_tasks:
            print("\n✓ COMPLETED TASKS:")
            for task in self.completed_tasks:
                status_icon = "✓" if task["status"] == "completed" else "?"
                print(f"  {status_icon} {task['title']}: {task['points']} points")
        
        if self.failed_tasks:
            print("\n✗ ISSUES ENCOUNTERED:")
            for task in self.failed_tasks:
                print(f"  ✗ {task['title']}: {task['error']}")
        self.check_remaining_tasks()
        print("\n" + "="*60)
        print(f"Rewards Automation Complete!")
        print("="*60 + "\n")
    
    def check_remaining_tasks(self):
        """Check for any remaining incomplete tasks and print their text"""
        try:
            print("\n" + "="*60)
            print("CHECKING FOR REMAINING INCOMPLETE TASKS")
            print("="*60)
            
            # Use the same XPath patterns to find remaining tasks
            xpath_patterns = [
                "//span[@aria-label='Points you will earn' and not(contains(@class, 'Lock'))]/../../../..",
                "//a[contains(@class, 'ds-card-sec')]//*[contains(@aria-label, 'Points in progress')]/../../../.."
            ]

            all_elements = []
            for pattern in xpath_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, pattern)
                    all_elements.extend(elements)
                except Exception:
                    continue
            
            # Remove duplicates
            unique_elements = list(dict.fromkeys(all_elements))
            
            remaining_tasks = []
            for idx, element in enumerate(unique_elements, 1):
                try:
                    aria_label = element.get_attribute("aria-label") or ""
                    print(f"[DEBUG] Element {idx} aria-label: '{aria_label}'")
                    # Skip frozen/locked tasks
                    if "locked" in aria_label.lower() or "frozen" in aria_label.lower() or "disabled" in aria_label.lower():
                        continue
                    elif "Points you will earn" in aria_label or "Points in progress" in aria_label or "Search on Bing" in aria_label or "earn" in aria_label.lower():
                        remaining_tasks.append(aria_label)
                    else:
                        element.click()
                except Exception:
                    continue
            
            if remaining_tasks:
                print(f"\n[!] Found {len(remaining_tasks)} remaining incomplete task(s):")
                for idx, aria_label in enumerate(remaining_tasks, 1):
                    print(f"  {idx}. {aria_label}")
                print(f"\n[!] These tasks were not processed - they may require manual completion.")
            else:
                print("\n[✓] No remaining incomplete tasks found!")
            
            print("="*60)
            
        except Exception as e:
            print(f"[⚠] Error checking remaining tasks: {e}")
            print("="*60)

if __name__ == "__main__":
    automator = BingRewardsAutomator()
    automator.run()
