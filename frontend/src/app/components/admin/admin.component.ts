import { Component, OnInit } from '@angular/core';
import { AdminService, Dish, MissingDish } from '../../services/admin.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.css']
})
export class AdminComponent implements OnInit {
  dishes: Dish[] = [];
  missingDishes: MissingDish[] = [];
  activeTab: 'dishes' | 'missing' = 'dishes';
  showAddDishModal = false;
  loading = false;
  error: string | null = null;

  newDish = {
    dish_name: '',
    country: '',
    ingredients: [] as any[]
  };

  // For ingredient search
  searchQuery = '';
  searchResults: any[] = [];
  searchingUsda = false;

  constructor(private adminService: AdminService) {}

  ngOnInit() {
    this.loadDishes();
    this.loadMissingDishes();
  }

  loadDishes() {
    this.loading = true;
    this.adminService.getDishes().subscribe({
      next: (response) => {
        this.dishes = response.dishes;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load dishes: ' + err.message;
        this.loading = false;
      }
    });
  }

  loadMissingDishes() {
    this.adminService.getMissingDishes().subscribe({
      next: (response) => {
        this.missingDishes = response.missing_dishes;
      },
      error: (err) => {
        console.error('Failed to load missing dishes:', err);
      }
    });
  }

  switchTab(tab: 'dishes' | 'missing') {
    this.activeTab = tab;
  }

  openAddDishModal() {
    this.showAddDishModal = true;
    this.newDish = {
      dish_name: '',
      country: '',
      ingredients: []
    };
    this.searchQuery = '';
    this.searchResults = [];
  }

  closeAddDishModal() {
    this.showAddDishModal = false;
  }

  searchUsda() {
    if (!this.searchQuery.trim()) {
      this.searchResults = [];
      return;
    }

    this.searchingUsda = true;
    this.adminService.searchUsda(this.searchQuery).subscribe({
      next: (response) => {
        this.searchResults = response.results;
        this.searchingUsda = false;
      },
      error: (err) => {
        console.error('USDA search failed:', err);
        this.searchingUsda = false;
      }
    });
  }

  addIngredient(result: any) {
    this.newDish.ingredients.push({
      name: result.name,
      usda_fdc_id: result.fdc_id,
      weight_g: 100 // Default weight
    });
    this.searchQuery = '';
    this.searchResults = [];
  }

  removeIngredient(index: number) {
    this.newDish.ingredients.splice(index, 1);
  }

  saveDish() {
    if (!this.newDish.dish_name || !this.newDish.country || this.newDish.ingredients.length === 0) {
      alert('Please fill in all fields and add at least one ingredient');
      return;
    }

    this.loading = true;
    this.adminService.createDish(this.newDish).subscribe({
      next: (response) => {
        alert('Dish added successfully!');
        this.closeAddDishModal();
        this.loadDishes();
        this.loading = false;
      },
      error: (err) => {
        alert('Failed to add dish: ' + err.message);
        this.loading = false;
      }
    });
  }
}
